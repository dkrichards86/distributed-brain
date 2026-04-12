# CRDTs (Conflict-free Replicated Data Types)

Data structures that can be replicated across nodes and merged automatically without coordination, guaranteeing eventual consistency by construction.

## Why it matters

In an eventually consistent distributed system, concurrent writes to the same data on different nodes create conflicts. Most conflict resolution strategies (last-write-wins, application merges) are ad-hoc and error-prone. CRDTs solve this at the data structure level — the merge operation is mathematically guaranteed to produce the same result regardless of the order or number of times it's applied.

## How it works

A CRDT defines a **merge function** that is:
- **Commutative** — `merge(A, B) = merge(B, A)` (order doesn't matter)
- **Associative** — `merge(merge(A, B), C) = merge(A, merge(B, C))` (grouping doesn't matter)
- **Idempotent** — `merge(A, A) = A` (applying twice has no extra effect)

Any merge function with these properties will converge to the same state on all nodes, regardless of network delays or message reordering.

### State-based CRDTs (CvRDTs)

Nodes periodically gossip their full state to peers. Each node merges incoming state with its own using the merge function.

**Examples:**

- **G-Counter (grow-only counter)** — each node maintains its own counter slot; the value is the sum of all slots; increment only touches your slot; merge takes the max per-slot. Result: a counter that only increases, with no coordination required.
- **PN-Counter** — two G-Counters (one for increments, one for decrements); value is sum(P) − sum(D)
- **G-Set (grow-only set)** — set union is the merge; elements can only be added, never removed
- **LWW-Element-Set** — each element carries a timestamp; merge takes the element with the higher timestamp; enables removal at the cost of clock dependency
- **OR-Set (observed-remove set)** — each addition gets a unique tag; removal removes only the specific tagged instances seen at removal time; handles add-after-remove correctly without clocks

### Operation-based CRDTs (CmRDTs)

Instead of shipping full state, nodes broadcast the operations themselves. The messaging layer must guarantee at-least-once delivery and exactly-once application (deduplication). Often more efficient for large state, but requires more infrastructure.

### Applications

- **Collaborative editing** — text CRDTs (LOGOOT, LSEQ, RGA) allow multiple users to edit the same document concurrently; merges produce correct results without operational transforms
- **Shopping carts** — add-only or LWW set semantics; Dynamo's original paper used CRDTs for cart merging
- **Distributed counters** — analytics systems use PN-Counters for distributed impression/event counting
- **Riak** — built-in CRDT support for counters, sets, maps, and flags

## Key tradeoffs

- **Limited semantics** — not all data structures map cleanly to CRDTs; strongly ordered, relational, or referentially constrained data typically cannot be expressed as a CRDT
- **Metadata overhead** — CRDTs often carry causal metadata (vector clocks, unique tags) that can be significantly larger than the payload; OR-Sets in particular can accumulate tombstones
- **No strong consistency** — CRDTs guarantee convergence, not linearizability; they're the right tool for AP systems, not CP systems
- **Removal complexity** — removing elements reliably requires careful design (OR-Set, tombstones) and periodic garbage collection

## Related concepts

- [Consistency Models](Consistency%20Models.md) — CRDTs implement eventual consistency by construction; they're incompatible with strong consistency requirements
- [Replication](Replication.md) — CRDTs are used in multi-leader and leaderless replication to resolve write conflicts without coordination
- [Logical Clocks](../Distributed%20Systems/Logical%20Clocks.md) — many CRDTs use version vectors or causal metadata to correctly handle concurrent operations
- [CAP Theorem](../Distributed%20Systems/CAP%20Theorem.md) — CRDTs are an AP strategy; they remain available and eventually consistent rather than sacrificing availability for strong consistency
