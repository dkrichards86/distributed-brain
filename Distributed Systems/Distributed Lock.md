# Distributed Lock

A mutual exclusion mechanism that prevents multiple nodes in a distributed system from concurrently executing a critical section.

## Why it matters

Shared resources — database rows, files, external API quotas, a singleton job — require exclusive access during modification. Process-local locks don't work across nodes. Distributed locks extend mutual exclusion across the network, allowing coordination without requiring all access to route through a single process.

## How it works

A node acquires the lock by writing a unique token to a shared store with a TTL:

- **Redis** — `SET key token NX PX <ttl>` atomically sets the key only if it doesn't exist; the TTL ensures the lock is released if the holder crashes
- **ZooKeeper / etcd** — the node creates an ephemeral node; the node auto-deletes when the session expires (heartbeat stops), releasing the lock
- **Raft-backed store** — write the lock entry via a linearizable write to an etcd or Consul cluster; the quorum guarantees the write is visible to all nodes before returning

The holder includes its token in any guarded operations. On release, it deletes the key **only if the token matches** (via a Lua script in Redis, or a compare-and-delete). This prevents a stale holder whose lock expired from releasing a lock held by another node.

**Fencing tokens:** a monotonically increasing number issued with each lock grant. Downstream resources (e.g., a database) reject writes from holders presenting a fencing token lower than the most recently seen one. This is the only reliable defense against a slow holder whose TTL expired but whose process hasn't noticed yet.

## Key tradeoffs

- TTLs introduce a window where two holders briefly overlap: if the holder pauses (GC, VM migration) longer than the TTL, a new holder acquires the lock while the original is still running; fencing tokens on downstream resources are the only safe defense
- The lock store is a single point of failure; using a replicated store (etcd, Consul, Redlock across multiple Redis instances) adds complexity and still has documented edge cases under clock skew
- Distributed locks reduce throughput; optimistic concurrency control ([MVCC](../Databases/MVCC.md), compare-and-swap) is preferable when conflicts are rare

## Related concepts

- [Quorum](Quorum.md) — lock stores backed by Raft or Redlock use quorum writes to ensure the lock acquisition is durably recorded before returning
- [Consensus Algorithms](Consensus%20Algorithms.md) — etcd and Consul implement distributed locks on top of Raft; the consensus layer ensures the lock state is consistent across replicas
- [Leader Election](Leader%20Election.md) — leader election is a special case of a distributed lock: acquiring the "leader" lock and holding it via heartbeats
- [Raft](Raft.md) — etcd uses Raft to replicate lock state; a lock acquired via a linearizable etcd write is safe because Raft ensures a quorum has agreed
- [MVCC](../Databases/MVCC.md) — an alternative to locking; uses version numbers instead of exclusive access to detect conflicts
