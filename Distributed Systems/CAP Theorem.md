# CAP Theorem

A distributed system can satisfy at most two of three properties — Consistency, Availability, and Partition tolerance — simultaneously.

## Why it matters

Network partitions are unavoidable in any system that spans multiple machines. CAP forces an explicit choice: when nodes can't communicate, does the system refuse requests to stay correct, or keep serving requests and risk returning stale or conflicting data? Making this choice deliberately — and exposing it as a tunable — is the difference between a system with predictable behavior and one with surprising failures.

## How it works

The three properties:

- **Consistency (C)** — every read returns the most recent write, regardless of which node handles it (linearizability)
- **Availability (A)** — every request receives a non-error response
- **Partition tolerance (P)** — the system continues operating when network partitions isolate nodes from each other

Since network partitions are unavoidable in practice, P is non-negotiable. The real choice is between **CP** and **AP**:

| Choice | Behavior during a partition |
|---|---|
| **CP** | Refuse reads/writes rather than risk serving stale or inconsistent data |
| **AP** | Continue serving requests, possibly with stale or divergent data that must be reconciled later |

Examples:
- **CP:** HBase, ZooKeeper, etcd, Spanner
- **AP:** Cassandra (default), DynamoDB (default reads), CouchDB

Many systems expose this as a per-request knob rather than a fixed choice — DynamoDB's `ConsistentRead` flag and Cassandra's consistency levels let you pay for CP only where the application demands it.

## Key tradeoffs

- **CP systems during a partition** — the minority partition must stop accepting writes; the system becomes partially unavailable to prevent split-brain
- **AP systems during a partition** — all nodes stay available but may accept conflicting writes; conflict resolution is deferred (last-write-wins, CRDTs, application merging)
- **CAP's "C" is specifically linearizability** — weaker consistency models (causal, read-your-writes) don't map cleanly to CAP; see [Consistency Models](../Databases/Consistency%20Models.md) for the full spectrum

## Related concepts

- [PACELC](PACELC.md) — extends CAP to cover the non-partition case: even when healthy, there's a latency/consistency tradeoff
- [Consistency Models](../Databases/Consistency%20Models.md) — the spectrum of consistency guarantees; CAP's C is the strongest point on that spectrum
- [Consensus Algorithms](Consensus%20Algorithms.md) — the mechanism CP systems use to stay consistent during partitions
- [Distributed Transactions](Distributed%20Transactions.md) — 2PC is CP: it blocks (sacrifices availability) rather than allow inconsistency
- [CRDTs](../Databases/CRDTs.md) — an AP strategy; CRDTs stay available and converge eventually rather than sacrificing availability for strong consistency
- [Replication](../Databases/Replication.md) — replication across nodes creates the consistency problem CAP describes
