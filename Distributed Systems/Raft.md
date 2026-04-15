# Raft

A consensus algorithm that replicates a log across a cluster of nodes by electing a single leader per term, having that leader sequence all writes, and committing entries once a majority of nodes have acknowledged them.

## Why it matters

Paxos is notoriously difficult to implement correctly — the original paper leaves critical engineering details unspecified, and "Multi-Paxos" (the variant needed for a replicated log) required years of engineering folklore to get right. Raft was designed with understandability as an explicit goal, decomposing the problem into three separable subproblems: leader election, log replication, and safety. This made it the default choice for new consensus implementations: etcd, Consul, CockroachDB, TiKV, and ScyllaDB all use Raft.

## How it works

### Roles and terms

Each node is in one of three states: **follower**, **candidate**, or **leader**. Time is divided into **terms** — monotonically increasing integers that act as a logical epoch. Every message carries the sender's term; a node that receives a higher term immediately reverts to follower and updates its own term. Terms prevent stale leaders from accepting writes after a new leader is elected.

### Leader election

Followers expect a periodic heartbeat (empty `AppendEntries` RPC) from the leader. If none arrives within the **election timeout** (randomized, typically 150–300ms), the follower:

1. Increments its term, transitions to candidate, votes for itself
2. Sends `RequestVote` RPCs to all other nodes

A node grants a vote if:
- The candidate's term is ≥ its own, **and**
- The candidate's log is at least as up-to-date as its own (compared by last log term, then last log index)

The second condition is the **election restriction** — it ensures a newly elected leader always has all committed entries, so no committed data is ever lost on a leadership change.

A candidate that receives votes from a majority wins and immediately starts sending heartbeats to suppress new elections. Randomized timeouts make it unlikely that two candidates start elections simultaneously, and if a split vote occurs, timeouts fire again at different times to break the tie.

### Log replication

The leader receives writes from clients. It appends each write to its local log as a new entry (with its current term number) and then sends `AppendEntries` RPCs to all followers in parallel.

An entry is **committed** once the leader has received acknowledgment from a majority of nodes (including itself). The leader then applies it to its state machine and responds to the client. Followers learn the commit index from subsequent `AppendEntries` messages and apply entries up to that index.

**Log matching property:** if two logs contain an entry with the same index and term, all entries up to that index are identical in both logs. Raft enforces this by including the previous entry's index and term in every `AppendEntries`; followers reject the append if their log doesn't match, and the leader walks back to find the divergence point and resends from there.

### Safety: the key invariant

A leader commits an entry only when a majority has it. An election only succeeds if the winner's log is at least as up-to-date as a majority of voters. These two rules together guarantee that a newly elected leader always has all previously committed entries — the core safety property of the algorithm.

One subtlety: a leader can only commit entries from **its own term** by counting replicas. Entries from previous terms are committed indirectly when a new entry from the current term is committed and all preceding entries are implicitly committed with it.

### Log compaction (snapshots)

Logs grow indefinitely. Periodically, each node takes a **snapshot** — a point-in-time image of the state machine — and discards the log entries before the snapshot's last included index. When a new or lagging follower needs entries the leader has already discarded, the leader sends the snapshot directly via `InstallSnapshot` RPC instead of replaying the missing log.

### Membership changes

Adding or removing nodes naively can create two independent majorities during the transition. Raft addresses this with **joint consensus**: the cluster temporarily operates under a transitional configuration that requires agreement from both the old and new majority before completing the change. Simpler implementations use a **single-server change** approach — adding or removing one node at a time, which can never create two independent majorities.

## Key tradeoffs

- **Leader is the bottleneck** — all writes go through a single leader; write throughput is bounded by that node's capacity and the round-trip time to a quorum; this is the inherent cost of strong consistency
- **Minority partition stalls** — the minority side of a network partition cannot make progress (no quorum); this is CP per [CAP theorem](CAP%20Theorem.md); the system chooses consistency over availability
- **Election latency on failure** — after a leader fails, the election timeout must expire before a new leader is elected; during this window the cluster is unavailable for writes; the timeout must be longer than the worst-case heartbeat jitter, but shorter than application-level timeouts
- **WAN latency multiplies commit cost** — in geo-distributed deployments, every write requires a round-trip to a majority across WAN; this makes Raft expensive for cross-region deployments unless read replicas are acceptable
- **Snapshot cost** — snapshotting a large state machine is expensive (serialize all state, write to disk); if snapshots are too infrequent, log replay on restart is slow; if too frequent, I/O pressure spikes

## Related concepts

- [Consensus Algorithms](Consensus%20Algorithms.md) — Raft is one of three consensus algorithms covered there (alongside Paxos and Zab); the note explains the common structure they all share
- [Leader Election](Leader%20Election.md) — Raft's term-based election mechanism is covered in detail there; it's the same algorithm
- [Replication](../Databases/Replication.md) — Raft implements strongly consistent log-based replication; CockroachDB and TiKV use it as the replication layer for each shard
- [Distributed Transactions](Distributed%20Transactions.md) — CockroachDB and TiKV use Raft per shard for replication and 2PC across shards for transactions; Raft replaces the need for a separate coordinator failover mechanism
- [Failure Detection](../Fault%20Tolerance/Failure%20Detection.md) — the election timeout is a fixed-timeout failure detector; missed heartbeats trigger elections; the timeout must be tuned to the network's heartbeat variance
- [Logical Clocks](Logical%20Clocks.md) — terms are a form of logical epoch/clock; they establish a total ordering of leadership periods and ensure stale leaders are recognized as such
- [CAP Theorem](CAP%20Theorem.md) — Raft is a CP system; the minority partition stalls rather than serving potentially inconsistent data
- [Service Discovery](../Architecture/Service%20Discovery.md) — etcd and Consul use Raft to replicate their service registry state; this is why they can be trusted as a source of truth for cluster membership
