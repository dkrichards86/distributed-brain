# LSM Trees

A write-optimized storage structure that batches writes in memory and flushes them to immutable sorted files on disk, merging those files in the background.

## Why it matters

[B-trees](B-Trees.md) do in-place updates — every write requires a random disk seek to the right page. On write-heavy workloads this becomes a bottleneck. LSM trees convert random writes into sequential writes, which are an order of magnitude faster on both spinning disks and SSDs. This makes them the storage engine of choice for databases that need to absorb high write throughput: RocksDB, Cassandra, LevelDB, and [DynamoDB](DynamoDB/DynamoDB%20Query%20Patterns.md) all use LSM trees internally.

## How it works

### The write path

1. Writes land in an in-memory buffer called a **MemTable** — an ordered data structure (usually a red-black tree or skip list) that keeps keys sorted
2. When the MemTable reaches a size threshold, it's flushed to disk as an immutable **SSTable** (Sorted String Table) — a file where key-value pairs are stored in sorted key order
3. A new empty MemTable takes its place; writes continue without waiting for any merge

### The read path

To read a key, the engine checks:
1. The active MemTable
2. Any in-memory MemTable flush buffers
3. SSTables on disk, newest first

Because multiple SSTables may contain versions of the same key, reads must check several files. [Bloom filters](../Algorithms/Bloom%20Filters.md) on each SSTable let the engine skip files that definitely don't contain the key.

### Compaction

SSTables accumulate over time. Background **compaction** merges multiple SSTables into a new, larger one — deduplicating versions, removing tombstoned (deleted) records, and restoring read efficiency. The compaction strategy trades off write amplification against read amplification:

| Strategy | How it works | Best for |
|---|---|---|
| **Leveled** (LevelDB, RocksDB) | SSTables organized into levels; L0→L1→... merges keep each level sorted | Read-heavy; bounded space amplification |
| **Size-tiered** (Cassandra) | Merges similarly-sized SSTables together | Write-heavy; more space amplification |
| **FIFO** | Oldest SSTables are evicted when storage threshold is hit | Time-series with TTLs; no compaction CPU cost |

### Deletes

Deletes don't remove data immediately — they write a **tombstone** marker. The tombstone shadows older versions during reads. The actual data is removed when compaction processes the tombstone.

## Key tradeoffs

- **Write amplification** — data is written multiple times: once to the WAL, once to the MemTable flush, and again during each compaction level; compaction CPU and I/O compete with foreground reads
- **Read amplification** — a single read may need to check many SSTables before finding the key; bloom filters reduce but don't eliminate this
- **Space amplification** — stale versions and tombstones accumulate between compactions; a key deleted today may not be physically reclaimed for minutes or hours
- **Read vs. write optimization** — leveled compaction improves read performance at the cost of more compaction I/O; size-tiered reduces compaction but degrades reads over time

## Related concepts

- [B-Trees](B-Trees.md) — the alternative storage engine; B-trees favor reads and in-place updates while LSM trees favor write throughput
- [Bloom Filters](../Algorithms/Bloom%20Filters.md) — used per-SSTable to short-circuit reads that would find nothing
- [Write-Ahead Logging](Write-Ahead%20Logging.md) — LSM trees use a WAL to make MemTable writes durable before the flush to SSTable
- [ClickHouse Architecture](ClickHouse/ClickHouse%20Architecture.md) — ClickHouse's MergeTree engine shares LSM concepts (immutable writes, background merging, deferred deletes) but is column-oriented and writes directly to disk rather than buffering in a MemTable
- [ClickHouse Parts](ClickHouse/ClickHouse%20Parts.md) — Parts are the ClickHouse analog to SSTables: immutable, created per-write, consolidated by background merging
