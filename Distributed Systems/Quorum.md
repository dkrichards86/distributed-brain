# Quorum

The minimum number of nodes that must agree on an operation for it to be considered valid in a distributed system.

## Why it matters

When data is replicated across N nodes, individual nodes can fail or become partitioned. A quorum ensures that any two groups of nodes that each form a quorum must overlap by at least one node — which guarantees that acknowledged writes are visible to subsequent reads even when some nodes are unavailable.

## How it works

For a cluster of N nodes, the standard majority quorum is ⌊N/2⌋ + 1. A write is accepted when W nodes acknowledge it; a read is served when R nodes respond. Setting **W + R > N** ensures read-write overlap: any read quorum must intersect any write quorum by at least one node, so the latest write is always present in a read.

Common tuning:
- **W = N, R = 1** — maximum durability, slow writes, fast reads
- **W = 1, R = N** — fast writes, slow reads, poor durability
- **W = R = ⌊N/2⌋ + 1** — balanced; tolerates up to ⌊N/2⌋ failures on both sides

[Consensus algorithms](Consensus%20Algorithms.md) such as Raft use quorums to commit log entries: an entry is committed once a majority of nodes have replicated it. [Leaderless replication](../Databases/Replication.md) systems (Cassandra, Dynamo) expose W and R directly as per-operation parameters.

## Key tradeoffs

- Quorum reads and writes require coordinating across multiple nodes, adding latency proportional to the slowest node in the quorum
- If too many nodes fail to form a quorum, the system becomes unavailable — a cluster of N tolerates at most ⌊N/2⌋ failures
- Leaderless quorum systems can have concurrent writes land on overlapping sets; without a tiebreaker, conflicts require resolution strategies (last-write-wins, [CRDTs](../Databases/CRDTs.md))

## Related concepts

- [Replication](../Databases/Replication.md) — quorum is the mechanism behind leaderless (Dynamo-style) replication; W and R are its primary dials
- [Consensus Algorithms](Consensus%20Algorithms.md) — all practical consensus algorithms (Raft, Paxos, Zab) commit decisions when a quorum agrees; a quorum is what gives them fault tolerance
- [Raft](Raft.md) — an entry is committed once the leader receives acknowledgment from a quorum; elections require a quorum of votes
- [Leader Election](Leader%20Election.md) — leader election requires a quorum to prevent split-brain; the winning candidate must receive votes from a majority
- [Distributed Lock](Distributed%20Lock.md) — distributed locks built on Raft or Redlock depend on quorum writes for correctness
- [CAP Theorem](CAP%20Theorem.md) — quorum systems are CP: if a quorum can't be reached, the system blocks rather than serving potentially stale data
