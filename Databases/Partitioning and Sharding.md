# Partitioning and Sharding

Splitting a dataset across multiple nodes so that each node owns a subset of the data, enabling horizontal scale beyond what a single machine can hold or serve.

## Why it matters

A single node has bounded storage, CPU, and I/O capacity. Partitioning allows a dataset to grow arbitrarily by adding nodes, and distributes read/write load across the cluster. Without it, vertical scaling (bigger hardware) hits a ceiling and creates a single point of failure.

## How it works

### Key-range partitioning

Data is sorted by key and divided into contiguous ranges — each partition owns a range (e.g., A–M, N–Z). The node responsible for a range is looked up in a routing table.

- **Pro:** supports efficient range scans; keys in the same range are co-located on one node
- **Con:** sequential key patterns (timestamps, auto-increment IDs) concentrate writes on the most recent partition — a **hot partition**

### Hash partitioning

`hash(key) % N` assigns each key to a node. Distributes keys uniformly regardless of access pattern.

- **Pro:** eliminates hot spots caused by sequential keys
- **Con:** destroys sort order — range queries require scatter-gather across all partitions

### Consistent hashing

A refinement of hash partitioning that maps keys and nodes onto a ring. Each key is assigned to the first node clockwise from its hash. When a node is added or removed, only the keys it was responsible for need to move — typically `1/N` of all keys.

See [Consistent Hashing](../Algorithms/Consistent%20Hashing.md) for the full mechanism. Used by Cassandra, DynamoDB, and Riak.

### Directory-based partitioning

A central lookup service maps each key (or key range) to its current node. Fully flexible — any key can be moved to any node by updating the directory.

- **Pro:** maximum flexibility for rebalancing
- **Con:** the directory is a coordination bottleneck and single point of failure; must itself be replicated

### Rebalancing

When nodes are added or removed, keys must be redistributed. Strategies:

- **Fixed number of partitions** — create far more partitions than nodes (e.g., 1,000 partitions on 10 nodes); when a node joins, it takes some partitions from existing nodes without re-hashing all keys
- **Dynamic partitioning** — partitions split when they exceed a size threshold and merge when they shrink; HBase and RocksDB use this
- **Consistent hashing ring** — adding a node only moves keys from its successor

### Secondary indexes with partitioning

Secondary indexes complicate partitioning because an index entry and the document it refers to may live on different partitions.

- **Local (scatter-gather) indexes** — each partition maintains its own local secondary index; queries must fan out to all partitions and merge results
- **Global indexes** — the secondary index is separately partitioned (by index key); a write to any document may need to update the global index on a different node, requiring coordination

## Key tradeoffs

- **Range vs. hash** — range partitioning enables efficient scans but is vulnerable to hot spots from sequential writes; hash partitioning is hot-spot resistant but kills range query efficiency
- **Rebalancing cost** — moving partitions between nodes generates significant I/O and network traffic; large data volumes make rebalancing slow and disruptive
- **Cross-partition operations** — [distributed transactions](../Distributed%20Systems/Distributed%20Transactions.md) across partitions are expensive; schema design should minimize the need for cross-partition reads and writes
- **Hot partitions** — even with good partitioning, a single hot key concentrates load on one node; must be mitigated at the application level (key salting, fan-out writes)

## Related concepts

- [Consistent Hashing](../Algorithms/Consistent%20Hashing.md) — the standard partitioning scheme for leaderless distributed databases
- [Replication](Replication.md) — each partition is typically replicated across multiple nodes for fault tolerance; partitioning and replication are configured together
- [Distributed Transactions](../Distributed%20Systems/Distributed%20Transactions.md) — transactions that touch multiple partitions require distributed coordination
- [DynamoDB Hot Partitions](DynamoDB/DynamoDB%20Hot%20Partitions.md) — a real-world example of hot partition problems under hash-based partitioning
