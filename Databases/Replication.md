# Replication

Maintaining copies of data on multiple nodes so the system can survive node failures and distribute read load.

## Why it matters

A single node is a single point of failure. Replication provides redundancy — if a node dies, another copy of the data exists. As a secondary benefit, reads can be spread across replicas to increase read throughput. The challenge is that keeping multiple copies of mutable data consistent requires coordination, and every replication topology makes a different tradeoff between durability, availability, and consistency.

## How it works

### Leader-follower (primary-replica)

One node is designated the **leader** and accepts all writes. The leader ships changes to **followers**, which apply them in order. Reads can go to either the leader (strongly consistent) or followers (potentially stale).

This is the default model in Postgres, MySQL, and most managed databases. Postgres streams its [WAL](Write-Ahead%20Logging.md) to replicas; each replica replays the log to stay in sync.

**Failover:** if the leader fails, a follower must be promoted. This requires detecting the failure (tricky — network partition vs. actual crash?) and electing a new leader without split-brain (two nodes both believing they're the leader).

### Synchronous vs. asynchronous replication

| Mode | Behavior | Tradeoff |
|---|---|---|
| **Synchronous** | Leader waits for at least one replica to confirm before acknowledging the write | No data loss on leader failure; write latency includes replica round-trip |
| **Asynchronous** | Leader acknowledges immediately; replicas catch up in the background | Low write latency; replica lag means potential data loss if leader crashes before replication |
| **Semi-synchronous** | Wait for one replica (quorum of 2); remaining replicas are async | Practical middle ground — one extra round-trip for durability |

### Replication lag

Asynchronous replicas are always slightly behind the leader. This is **replication lag** — the delay between a write landing on the leader and becoming visible on followers. Lag is usually milliseconds, but can grow to seconds or minutes under heavy write load or network issues.

Consequences:
- A read from a lagging replica returns stale data
- A user who just wrote to the leader and immediately reads from a replica may not see their own write ([read-your-writes consistency](Consistency%20Models.md))
- Monitoring lag is critical — a replica that's fallen hours behind is useless for failover

### Multi-leader replication

Multiple nodes accept writes. Changes from each leader are propagated to the others. This enables writes from multiple data centers (lower latency for geographically distributed users) and is used by multi-region active-active setups.

The hard problem: **write conflicts**. Two leaders may accept concurrent updates to the same row. Conflict resolution strategies include:
- Last write wins (LWW) — simple but can lose data
- Application-level merging — CRDT data structures that merge without conflicts
- Exposing conflicts to the application to resolve

### Leaderless replication (Dynamo-style)

No designated leader — any node can accept writes. The client writes to multiple nodes directly (or through a coordinator). Reads similarly query multiple nodes and take the most recent value.

**Quorum reads and writes:** with `N` replicas, a write to `W` nodes and a read from `R` nodes guarantees you see the latest write when `W + R > N`. Common setup: N=3, W=2, R=2.

Used by Cassandra, DynamoDB (internally), and Riak. Excellent availability but requires conflict resolution for concurrent writes.

## Key tradeoffs

- **Durability vs. write latency** — synchronous replication survives leader failure without data loss but every write pays a cross-node round-trip; async replication is fast but an unacknowledged write can be lost
- **Read scale vs. consistency** — routing reads to replicas increases throughput but serves potentially stale data; [consistency models](Consistency%20Models.md) formalize what staleness is acceptable
- **Failover complexity** — detecting leader failure and promoting a replica without split-brain or data loss is genuinely hard; managed databases (RDS, Cloud Spanner) hide this complexity at a cost
- **Replication lag monitoring** — a replica running far behind provides no durability value and may serve dramatically stale data; lag must be tracked and alerted on

## Related concepts

- [Write-Ahead Logging](Write-Ahead%20Logging.md) — the WAL is the replication stream in Postgres; physical replication ships WAL bytes directly
- [Consistency Models](Consistency%20Models.md) — replication lag is the source of consistency problems; the consistency model determines how the system handles it
- [Consistent Hashing](../Algorithms/Consistent%20Hashing.md) — used in leaderless systems to determine which nodes own which keys
- [DynamoDB Hot Partitions](DynamoDB/DynamoDB%20Hot%20Partitions.md) — DynamoDB uses leaderless replication internally; partitioning and replication interact
