# Sharding

Horizontal partitioning of a dataset across multiple independent database nodes, where each node owns a disjoint subset of the data.

## Why it matters

A single database node has bounded storage, CPU, and I/O. Once a dataset or write throughput exceeds what one machine can handle, vertical scaling (bigger hardware) hits a ceiling. Sharding distributes both data and load horizontally across many nodes, each of which is a full database instance — so the system can scale arbitrarily by adding nodes.

## How it works

### Shard key selection

Every row (or document) is assigned to exactly one shard by a **shard key**. The choice of shard key determines distribution quality and query efficiency:

- **Hash sharding** — `hash(key) % N` places rows uniformly across shards regardless of access pattern; destroys sort order, so range queries require scatter-gather
- **Range sharding** — contiguous key ranges go to the same shard; enables range queries within a shard but risks hot shards when writes are sequential (timestamps, auto-increment IDs)
- **Consistent hashing** — maps both keys and nodes onto a ring; adding or removing a node only redistributes `1/N` of keys; used by Cassandra, DynamoDB, and Riak — see [Consistent Hashing](../Algorithms/Consistent%20Hashing.md)
- **Directory-based sharding** — a central lookup table maps each key (or key range) to a shard; maximally flexible but the directory is a coordination bottleneck

### Routing

Clients or a routing proxy must direct queries to the correct shard. Common approaches:

- **Client-side routing** — client holds the shard map and connects directly to the right node
- **Proxy-based routing** — a stateless proxy (e.g., Vitess, ProxySQL, mongos) accepts queries and forwards them
- **Gossip / metadata service** — nodes advertise their key range; client queries any node and is redirected if necessary (Cassandra)

### Rebalancing

When shards are added or removed, data must move. Strategies:

- **Fixed partitions** — create far more logical shards than nodes (e.g., 1,000 shards on 10 nodes); adding a node steals shards without re-hashing
- **Dynamic splitting** — shards split when they exceed a size threshold; HBase and Spanner use this
- **Consistent hashing ring** — adding a node only moves keys from its successor

### Secondary indexes

Secondary indexes complicate sharding because the indexed field may not be the shard key:

- **Local indexes** — each shard maintains its own secondary index; queries that can't be routed by shard key must scatter-gather across all shards and merge
- **Global indexes** — the index is separately sharded by index key; writes may update an index shard different from the data shard, requiring coordination

## Key tradeoffs

- **Range vs. hash** — hash sharding prevents hot spots from sequential keys but kills range scan efficiency; range sharding enables co-located range queries but must handle write skew
- **Cross-shard operations** — joins, transactions, and aggregations across shards are expensive; [distributed transactions](../Distributed%20Systems/Distributed%20Transactions.md) are required for atomicity; schema design should minimize cross-shard access
- **Hot shards** — even with good sharding, a single high-traffic key concentrates load on one shard; mitigated with key salting or fan-out writes
- **Rebalancing cost** — moving shards generates significant I/O and network traffic; large datasets make rebalancing slow and disruptive
- **Operational complexity** — each shard is an independent DB instance; schema migrations, backups, and monitoring multiply with shard count

## Related concepts

- [Partitioning](Partitioning.md) — partitioning divides data within a single node; sharding extends horizontal partitioning across multiple nodes
- [Federation](Federation.md) — federation splits by entity type (different schemas per node) rather than by row; the two are often combined
- [Consistent Hashing](../Algorithms/Consistent%20Hashing.md) — the standard key assignment scheme for leaderless sharded databases
- [Replication](Replication.md) — each shard is independently replicated for fault tolerance; sharding and replication are configured together
- [Distributed Transactions](../Distributed%20Systems/Distributed%20Transactions.md) — transactions touching multiple shards require distributed coordination
- [DynamoDB Hot Partitions](DynamoDB/DynamoDB%20Hot%20Partitions.md) — a real-world example of hot shard problems under hash-based sharding
- [UUID](../Distributed%20Systems/UUID.md) — v4 UUIDs distribute writes uniformly across hash shards; v7 and Snowflake IDs trade that for time-sortability
- [Snowflake ID](../Distributed%20Systems/Snowflake%20ID.md) — time-prefixed IDs create sequential write hot spots in range-sharded systems
