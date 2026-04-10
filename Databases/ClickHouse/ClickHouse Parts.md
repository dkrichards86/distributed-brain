# ClickHouse Parts

Physical storage units in [ClickHouse](ClickHouse%20Architecture.md) — each INSERT creates a new immutable directory on disk containing one file per column, a primary index, and any secondary indexes; background merging consolidates them over time.

## Why it matters

Parts are the unit of write in ClickHouse. Their count directly affects query latency (more parts = more directories to open and merge at query time) and background CPU load. Batching inserts and understanding the merge lifecycle is the primary operational lever for keeping ClickHouse healthy under write load.

## How it works

### Structure of a part

Each part is a directory containing:
- One `.bin` file per column (compressed column data)
- One `.mrk` file per column (granule mark offsets, used to seek into `.bin` files)
- `primary.idx` — the sparse primary key index (one mark per [granule](ClickHouse%20Granules.md))
- Index files for any data-skipping indexes
- `columns.txt`, `count.txt`, checksums — metadata

Parts are **immutable** once written. ClickHouse never modifies a part in place.

### Insert → part lifecycle

1. **INSERT** lands as a new part with a name encoding the [partition](ClickHouse%20Partitions.md) key and a sequence number (e.g., `20240101_1_1_0`).
2. **Background merging** (MergeTree engine) continuously selects groups of small parts within the same partition and merges them into a single larger part. The old parts are marked inactive and deleted after a retention window.
3. **Mutations** (UPDATE / DELETE) are applied asynchronously: ClickHouse rewrites affected parts with the mutation applied, then swaps the new part in and removes the old one.

### Part count and query latency

At query time, ClickHouse opens and reads the primary index of every part in the relevant partitions. More parts = more index reads before any data is scanned. ClickHouse enforces a soft limit (`max_parts_in_total`, default 100,000) and a hard limit; exceeding the soft limit slows inserts with a delay to let merges catch up.

**Rule of thumb:** aim for inserts that create parts of at least a few hundred MB each. Thousands of small parts (from row-by-row or very frequent small inserts) will degrade query performance noticeably.

### Monitoring part health

```sql
SELECT partition, count() AS part_count, sum(rows) AS total_rows
FROM system.parts
WHERE table = 'your_table' AND active
GROUP BY partition
ORDER BY partition;
```

High part counts per partition indicate inserts are arriving faster than merges can consolidate them.

## Key tradeoffs

- **Write throughput vs. part count** — high-frequency small inserts create many parts quickly; ClickHouse can absorb this temporarily but merging will lag under sustained load
- **Merge CPU vs. query latency** — background merging reduces part count and improves queries, but consumes I/O and CPU; too aggressive merging can starve queries
- **Immutability vs. update cost** — immutable parts enable high write throughput and simple crash recovery, but mutations (UPDATE/DELETE) require full part rewrites
- **Part size vs. merge cost** — larger parts take longer to merge and hold more data in the "stale" state during mutation; smaller parts merge faster but accumulate quicker

## Related concepts

- [LSM Trees](../LSM%20Trees.md) — Parts are the ClickHouse analog to SSTables: immutable files created per-write and consolidated by background merging; unlike SSTables, Parts are column-oriented directories written directly to disk with no MemTable buffer
