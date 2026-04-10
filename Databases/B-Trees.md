# B-Trees

A self-balancing tree data structure that stores many keys per node, minimizing disk reads by reducing tree height and aligning node size to storage page size.

## Why it matters

Binary search trees require O(log₂ n) node accesses to find a record. In memory that's fast; on disk each access is milliseconds. A million-row binary tree can be 20 levels deep — potentially 20 disk reads per lookup. B-trees solve this by packing hundreds of keys per node, reducing a million-row tree to 3–4 levels. This is why virtually every relational database uses B-trees (specifically B+ trees) for indexes.

## How it works

### Why binary trees fail on disk

Each node access = one disk read. Disk reads are ~1000x slower than memory access. Unbalanced binary trees degrade to linked lists on skewed data — and real-world data is often skewed.

### The B-tree solution

Each node holds many keys (often hundreds) in sorted order, with pointers to child nodes between them. A node with keys `[10, 20, 30]` has four children: values < 10, values 10–20, values 20–30, values > 30.

Node size is tuned to match storage page size (typically 4KB–16KB). One disk read loads one full node with hundreds of keys — each I/O is more valuable.

### Staying balanced

All leaf nodes are always at the same depth. This guarantees O(log n) performance for every operation — no degenerate cases.

**Splits on insert:** When a node is full and a new key is inserted, the node splits in half. The middle key is promoted to the parent. If the parent is also full, it splits too, potentially cascading to the root. New levels are only added at the root, uniformly across the entire tree.

### B+ tree variant (used by most databases)

In a B+ tree:
- **Internal nodes** contain only keys for navigation — no data records
- **Leaf nodes** contain the actual data (or pointers to it)
- **Leaf nodes are linked** — you can scan forward through a range without returning to higher levels

This makes range queries (`BETWEEN`, `>`, `<`) especially efficient: find the start of the range, then follow the leaf chain.

### What this means for queries

| Access pattern | B-tree behavior |
|---|---|
| Primary key lookup | Single B-tree traversal — fast and consistent |
| Range query with index | Find start, scan leaf nodes — efficient |
| Full table scan | Bypasses B-tree entirely, reads raw pages |
| Composite index `(last, first)` | Supports queries on `last` alone or `(last, first)` — not `first` alone |

### Concurrent access

Multiple readers can traverse the tree simultaneously. Writers lock individual nodes rather than the whole tree, allowing good read-write concurrency.

## Key tradeoffs

- **Read performance vs. write overhead** — adding an index adds a B-tree to maintain; every insert/update/delete must update all applicable indexes, slowing writes proportionally
- **Node size vs. key count** — larger nodes mean fewer disk reads per lookup but more wasted I/O when only a few keys match; default page sizes are generally well-tuned
- **Composite index column order** — the first column gets binary search (O(log n)); subsequent columns get linear scan of the matching granules; put the most selective column first
- **Index count** — more indexes = faster reads for more access patterns, but slower writes and more storage; every index has to justify its cost

## Related concepts

- [Relational Databases](Relational%20Databases.md) — the primary use case for B-trees; virtually every relational database uses B+ trees for indexes
- [ClickHouse Indexing Strategies](ClickHouse/ClickHouse%20Indexing%20Strategies.md) — ClickHouse deliberately avoids B-tree row-level indexes in favor of sparse indexing and granule skipping

## My context

## Open questions

- How do SSDs change the B-tree optimization equation — are page-aligned reads still the right abstraction when random reads are fast?
- What's the actual fill factor databases use for B-tree nodes, and how does it affect insert performance on append-heavy workloads?
- How do [LSM trees](LSM%20Trees.md) (used by Cassandra, RocksDB) compare to B-trees for write-heavy workloads?
