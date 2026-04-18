# Logical Clocks

Mechanisms for ordering events in a distributed system without relying on synchronized physical clocks.

## Why it matters

Physical clocks on different machines drift and can't be perfectly synchronized. If you use wall-clock timestamps to order events across nodes, you can't tell whether event A truly happened before event B or just had a clock that ran ahead. Logical clocks capture the causal ordering of events — what happened before what — without requiring clock agreement.

## How it works

### Lamport timestamps

Each node maintains a counter. The rules:
1. Increment the counter before each event
2. When sending a message, attach the current counter value
3. When receiving a message, set your counter to `max(local, received) + 1`

This guarantees: if event A causally precedes event B, then `timestamp(A) < timestamp(B)`. The reverse is not guaranteed — equal or ordered timestamps don't imply a causal relationship.

Lamport timestamps give a **total order** on events, but it's a superset of the causal order. Unrelated events get arbitrary ordering.

### Vector clocks

Each node tracks a counter **per node** in the system. The rules:
1. Increment your own slot before each event
2. When sending a message, attach the full vector
3. When receiving a message, take the element-wise max of both vectors, then increment your slot

Comparison: vector `A < B` (A causally precedes B) if every element of A is ≤ the corresponding element of B, with at least one strictly less.

If neither `A < B` nor `B < A`, the events are **concurrent** — they happened without knowledge of each other. This is the key capability vector clocks add over Lamport timestamps: detecting concurrency, not just ordering.

Used in Dynamo-style databases to detect write conflicts that need resolution.

### Hybrid logical clocks (HLC)

Combines a physical timestamp with a logical counter. Stays close to wall time (useful for debugging and TTL semantics) while maintaining causal ordering even when physical clocks diverge slightly. Used in CockroachDB and YugabyteDB.

## Key tradeoffs

- **Lamport vs. vector** — Lamport is O(1) per message, vector is O(N) per message (N = number of nodes). Lamport orders everything; vector clocks distinguish causality from concurrency
- **Vector clock size** — vector clocks grow with cluster size; impractical for large dynamic clusters without pruning or version vectors
- **Causality vs. consistency** — tracking causal order enables [causal consistency](../Databases/Consistency%20Models.md) but doesn't give you linearizability; for that you need coordination via consensus

## Related concepts

- [Consistency Models](../Databases/Consistency%20Models.md) — causal consistency is defined by causal ordering; vector clocks are the mechanism for tracking it
- [Consensus Algorithms](Consensus%20Algorithms.md) — consensus establishes a total order on events, stronger than what Lamport timestamps alone provide
- [CRDTs](../Databases/CRDTs.md) — CRDTs use causal tracking (often version vectors) to merge concurrent writes without coordination
- [Distributed Transactions](Distributed%20Transactions.md) — ordering events across nodes is the core problem distributed transactions must solve
- [Snowflake ID](Snowflake%20ID.md) — embeds a physical millisecond timestamp; vulnerable to clock skew in a way logical clocks are not
- [UUID](UUID.md) — v7 UUIDs use a physical timestamp prefix for sortability, trading causal guarantees for practical ordering
