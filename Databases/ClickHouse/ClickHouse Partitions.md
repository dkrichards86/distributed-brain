# ClickHouse Partitions

Logical groupings of data within a [[ClickHouse Architecture|ClickHouse]] table — typically by time period — that enable partition pruning (skipping entire groups of parts at query time) and independent data lifecycle management.

## Why it matters

Partitions are the coarsest-grained filter in ClickHouse's query execution pipeline. A query with a partition-key predicate eliminates whole [[ClickHouse Parts|parts]] before the primary index is even consulted. For time-series workloads, good partitioning can reduce the data scanned by orders of magnitude. Partitions also make TTL expiry and manual data drops cheap — dropping a partition is an instant metadata operation, not a row-level delete.

## How it works

### Defining a partition key

```sql
CREATE TABLE events (
    tenant_id  UInt32,
    timestamp  DateTime,
    ...
) ENGINE = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (tenant_id, timestamp);
```

The `PARTITION BY` expression is evaluated for each row at insert time. Rows with the same partition key value are stored in the same partition. All [[ClickHouse Parts|parts]] within a partition share its key.

### Partition pruning at query time

When a `WHERE` clause filters on the partition key column, ClickHouse evaluates the partition expression against each partition's key range. Partitions that cannot satisfy the predicate are skipped entirely — their parts are never opened.

```sql
-- This prunes all partitions except 2024-01
SELECT count() FROM events WHERE toYYYYMM(timestamp) = 202401;
```

Pruning is **only effective when the query filter can be resolved against the partition expression**. Filtering on a non-partition column provides no partition-level skip benefit.

### Partition count limits

Each partition maps to at least one part on disk. Partition metadata (list of parts per partition) is held in memory. Too many partitions causes:
- Slow `INSERT` (more metadata to update)
- Slow `SELECT` (more partition metadata to scan even before pruning)
- Slow DDL operations (`ALTER TABLE`, `OPTIMIZE`)

**Recommended range: 10–1,000 active partitions.** Monthly partitioning (`toYYYYMM`) is the most common safe default. Daily partitioning (`toYYYYMMDD`) is fine for tables with a small retention window but can accumulate thousands of partitions over years.

### Data lifecycle management

Dropping a partition is an O(1) metadata operation — no row-level deletion, no merge required:

```sql
ALTER TABLE events DROP PARTITION '202312';
```

This makes partition-based TTL and retention policies operationally cheap compared to row-level deletes (which require async mutations and part rewrites).

### Partitions vs. sharding

Partitions are a **local** concept — they split data within a single node's storage. They are unrelated to distributed sharding across nodes. On a distributed ClickHouse cluster, sharding and partitioning are independent axes of data organization.

## Key tradeoffs

- **Pruning effectiveness vs. partition count** — finer partitions (daily) prune more aggressively per query but accumulate faster and inflate metadata; coarser partitions (monthly) are safer operationally but require scanning more data per partition
- **Drop speed vs. granularity** — you can only drop at partition granularity; if partition = month, you can't cheaply expire a single week's data
- **Parallelism** — ClickHouse can process multiple partitions in parallel; too few partitions (e.g., one large one) limits parallelism on multi-core hardware
- **Partition key lock-in** — changing the partition key requires rewriting the entire table
