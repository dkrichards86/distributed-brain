# Leader Election

The process by which a cluster of nodes selects a single coordinator to act on behalf of the group.

## Why it matters

Many distributed operations are simpler with a single authoritative node — accepting writes, sequencing operations, holding locks, or coordinating a transaction. Without a protocol to agree on who the leader is, multiple nodes may act as leader simultaneously (split-brain), corrupting shared state. Leader election ensures at most one node believes it holds authority at any time.

## How it works

### Term-based election (Raft-style)

Nodes track a **term** number — a monotonically increasing counter that acts as a logical epoch. When a node suspects the leader has failed (election timeout fires with no heartbeat received), it:

1. Increments its term and transitions to **candidate** state
2. Votes for itself and sends `RequestVote` RPCs to all other nodes
3. A node grants a vote if the candidate's term is higher than its own and the candidate's log is at least as up-to-date as its own
4. The candidate wins if it receives votes from a majority; it immediately begins sending heartbeats to suppress further elections

Crucially, a node that receives a message with a higher term immediately reverts to **follower** — this prevents stale leaders from accepting writes after a new leader is elected.

### Bully algorithm

Simpler but less safe. When a node detects the leader is unreachable, it sends an election message to all nodes with higher IDs. If no response, it declares itself leader. If a higher-ID node responds, it takes over the election. The node with the highest ID always wins.

Problem: doesn't handle network partitions correctly — the highest-ID node in a minority partition can declare itself leader, creating split-brain.

### External coordination (ZooKeeper / etcd)

Nodes compete to create an ephemeral node (a node that auto-deletes when the creator's session expires) at a fixed path. The node that succeeds is the leader. If the leader dies, its session expires, the ephemeral node is deleted, and the competition restarts.

This delegates election correctness to a separate consensus system, making the client-facing protocol simpler. Common pattern for Kafka controller election, Hadoop NameNode HA.

### Lease-based leadership

The leader acquires a time-bounded lease from a quorum of nodes. As long as the lease is valid, the leader can act without re-confirming its status on each operation. Before the lease expires, the leader must renew it.

Reduces coordination overhead but requires clock bounds — the leader must release its lease before `lease_duration + max_clock_drift` elapses to prevent two leaders overlapping.

## Key tradeoffs

- **Safety vs. availability** — a correct election protocol requires a quorum; if more than half the nodes are unreachable, no leader can be elected (no split-brain, but the system stalls)
- **Election latency** — detecting failure takes time (timeouts); re-election adds additional latency; during this window the system is leaderless and can't accept writes
- **Lease overhead vs. correctness** — leases reduce per-operation overhead but add clock-dependency; a clock jump can make two nodes simultaneously believe they're the leader

## Related concepts

- [Raft](Raft.md) — Raft's term-based election mechanism is the canonical example; the full algorithm shows why the log up-to-date check is essential for safety
- [Consensus Algorithms](Consensus%20Algorithms.md) — Raft and Zab embed leader election; the election protocol is inseparable from log replication safety
- [Failure Detection](../Fault%20Tolerance/Failure%20Detection.md) — election is triggered by failure detection; the accuracy of failure detection determines how quickly re-election happens and how often false elections fire
- [Replication](../Databases/Replication.md) — leader-follower replication requires leader election on failover; the new leader must have all committed log entries
- [CAP Theorem](CAP%20Theorem.md) — election protocols are CP: the system pauses writes during an election to avoid split-brain
- [Quorum](Quorum.md) — leader election requires a quorum of votes to prevent split-brain; no candidate can win without a majority
- [Distributed Lock](Distributed%20Lock.md) — leader election is a special case of a distributed lock; the "leader" is the holder of the lock, renewed via heartbeats or lease extensions
