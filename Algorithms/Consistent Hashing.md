# Consistent Hashing

A hashing scheme that minimizes key redistribution when nodes are added to or removed from a distributed system.

## Why it matters

Naive partitioning assigns keys to nodes using `hash(key) % N`. When N changes — a node is added or fails — almost every key maps to a different node. For a cache, this means a near-total miss storm. For a database, it means a massive rebalancing operation. Consistent hashing bounds the disruption: only the keys that *were* owned by the added/removed node need to move, typically `1/N` of all keys.

## How it works

### The ring

Both keys and nodes are hashed onto a conceptual ring of integers (0 to 2³²-1). A key is assigned to the **first node clockwise** from its position on the ring.

```
         Node A (hash: 100)
            ↑
... — key7 — key8 — [Node A] — key1 — key2 — [Node B] — key3 — ...
                                                   ↑
                                             Node B (hash: 250)
```

Adding a node only affects keys between it and its predecessor — those keys now map to the new node instead. Removing a node transfers its keys to its successor. All other keys are unaffected.

### Virtual nodes (vnodes)

A single physical node placed at one ring position creates uneven distribution — nodes end up with different key counts depending on where they land. **Virtual nodes** give each physical node multiple positions on the ring (often 100–200 per node).

Benefits:
- Distribution is statistically uniform across physical nodes
- When a node is removed, its load spreads across many successors rather than piling onto one neighbor
- Nodes with more capacity can be assigned more vnodes

### Replication

To replicate each key to `N` nodes, assign it to the first `N` nodes clockwise from its position. Adding replication to the ring doesn't change the hashing logic — just how many nodes each position writes to.

## Key tradeoffs

- **Distribution uniformity** — without vnodes, placement is random and variance is high; with vnodes the distribution is good but adding/removing a node requires moving more small key ranges
- **Hot spots from skewed access** — consistent hashing distributes *keys* evenly, not *traffic*; a single high-traffic key always lands on one node regardless of ring position; [DynamoDB Hot Partitions](../Databases/DynamoDB/DynamoDB%20Hot%20Partitions.md) is this problem in practice
- **Membership coordination** — all nodes must agree on the current ring state; this requires a gossip protocol or coordination service (ZooKeeper, etcd) to propagate membership changes
- **Not suitable for ordered scans** — because keys are hashed before placement, adjacent keys land on arbitrary nodes; range queries require scatter-gather across all nodes

## Related concepts

- [DynamoDB Hot Partitions](../Databases/DynamoDB/DynamoDB%20Hot%20Partitions.md) — consistent hashing distributes keys but skewed access patterns still create hot nodes
- [Bloom Filters](Bloom%20Filters.md) — another probabilistic structure used alongside consistent hashing in distributed systems to reduce unnecessary lookups
- [Replication](../Databases/Replication.md) — consistent hashing is commonly extended with replication factors to assign each key to multiple nodes
- [Partitioning and Sharding](../Databases/Partitioning%20and%20Sharding.md) — consistent hashing is one of several partitioning strategies; the note covers the full landscape including range and directory-based approaches
- [Gossip Protocols](../Distributed%20Systems/Gossip%20Protocols.md) — gossip propagates ring membership changes in consistent hashing-based systems like Cassandra
