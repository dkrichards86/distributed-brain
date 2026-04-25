# Consensus Algorithms

Protocols that allow a cluster of nodes to agree on a single value even when some nodes fail or messages are delayed.

## Why it matters

Many distributed system operations require agreement — which node is the leader, whether a transaction committed, what the next log entry is. Without a formal consensus protocol, concurrent proposals can lead to split-brain: two nodes both believing they're in charge, corrupting state. Consensus algorithms solve this with provable safety guarantees.

## How it works

All practical consensus algorithms share a common structure: a **proposer** suggests a value, **acceptors** vote, and a value is chosen when a **quorum** (majority) agrees. Once chosen, the value is permanent.

### Paxos

The foundational consensus algorithm. A single round of Paxos has two phases:

1. **Prepare** — the proposer sends a ballot number to acceptors; each acceptor promises not to accept lower-numbered ballots and returns any previously accepted value
2. **Accept** — the proposer sends its value (constrained by any previously accepted values from phase 1); acceptors accept if no higher ballot has been promised

Paxos is notoriously hard to implement correctly for a full replicated log (Multi-Paxos). The original paper left many engineering details underspecified.

### Raft

Designed as an understandable alternative to Paxos. Decomposes consensus into three subproblems:

- **Leader election** — one node is elected leader per term; the leader handles all writes
- **Log replication** — the leader appends entries to its log and replicates them to followers; an entry is committed once a majority acknowledges it
- **Safety** — a new leader must have all committed entries (guaranteed by the election rule: a node only votes for a candidate with a log at least as up-to-date as its own)

Raft's explicit leader and strict log ordering make it significantly easier to implement than Paxos. Used by etcd, CockroachDB, TiKV, and Consul.

### Zab (Zookeeper Atomic Broadcast)

The protocol behind ZooKeeper. Similar to Raft but designed specifically for primary-backup systems. Two modes:

- **Recovery mode** — elect a new leader and sync all followers to the leader's state
- **Broadcast mode** — leader sequences all writes and broadcasts them to followers; a write commits when a quorum acknowledges

Zab guarantees that all delivered messages are delivered in the same order on all nodes.

### Common properties

All three provide:
- **Safety** — no two nodes ever decide different values
- **Liveness** — the system makes progress as long as a majority of nodes are reachable
- **Fault tolerance** — a cluster of `2f + 1` nodes can tolerate `f` failures

## Key tradeoffs

- **Throughput vs. consistency** — every write requires a quorum round-trip; this is the unavoidable cost of linearizability
- **Leader bottleneck** — single-leader designs (Raft, Zab) serialize all writes through one node; this limits write throughput to one node's capacity
- **Partition behavior** — the minority partition cannot make progress (CP behavior per [CAP theorem](CAP%20Theorem.md)); this is the price of safety
- **Latency** — a commit requires at least one round-trip to a majority; geo-distributed clusters pay WAN latency on every write

## Related concepts

- [Raft](Raft.md) — deep-dive on Raft specifically: terms, log replication, the election restriction, snapshots, and membership changes
- [Leader Election](Leader%20Election.md) — Raft and Zab embed leader election; it's also used independently for coordination
- [Distributed Transactions](Distributed%20Transactions.md) — 2PC uses a coordinator that requires consensus-like agreement; Paxos/Raft can replace 2PC's coordinator
- [Replication](../Databases/Replication.md) — consensus-based replication is the foundation of strongly consistent distributed databases
- [CAP Theorem](CAP%20Theorem.md) — consensus algorithms implement the CP side of CAP; they sacrifice availability during partitions to maintain consistency
- [Failure Detection](../Fault%20Tolerance/Failure%20Detection.md) — consensus algorithms depend on failure detection to trigger leader re-election
- [Gossip Protocols](Gossip%20Protocols.md) — gossip is often used alongside consensus for cluster membership propagation
- [Quorum](Quorum.md) — the quorum (majority) is the core mechanism all consensus algorithms use to make decisions; a value is chosen when a quorum agrees
- [Distributed Lock](Distributed%20Lock.md) — distributed locks are implemented on top of consensus systems (etcd, Consul) to guarantee mutual exclusion
