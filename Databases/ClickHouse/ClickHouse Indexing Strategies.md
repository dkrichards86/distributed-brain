# ClickHouse Indexing Strategies

[ClickHouse](ClickHouse%20Architecture.md) provides three complementary indexing mechanisms — primary key, partition pruning, and data-skipping indexes — that work together to eliminate granules and parts from scans rather than enabling O(1) row lookups.

## Why it matters

ClickHouse has no traditional [B-tree](../B-Trees.md) row-level index. Instead it reduces I/O by skipping entire blocks of data. Knowing which indexing mechanisms exist, how they interact, and when each applies is the difference between a query that scans 100 granules and one that scans 10,000.

## How it works

### Primary key index (sparse index)

The primary key determines sort order on disk. ClickHouse writes one index mark per [granule](ClickHouse%20Granules.md) (8,192 rows by default), not per row — this is sparse indexing. The full index fits in memory.

**Query execution:** ClickHouse binary-searches the index to find candidate granule ranges, then scans only those granules. Rows outside the range are never read.

**Column order rules:**
- First column: binary search → O(log n) granules evaluated
- Second column: only useful when the first column's range is narrow (many rows share the same first-column value)
- Third+ columns: diminishing returns; index size grows, benefit shrinks
- Limit to 3–4 columns max

**Choosing the right first column:** the column that appears in the most `WHERE` clauses with equality or range filters. For event data, `(tenant_id, timestamp)` is common — tenant filters prune most granules; timestamp refines further within a tenant's data.

**Sorting key vs. primary key:** in ClickHouse these are usually the same, but you can have a sorting key that's a superset of the primary key. Additional sort columns don't add index marks but do colocate related rows, helping range scans.

### Partition pruning

[Partitions](ClickHouse%20Partitions.md) are a coarser filter applied before the primary index. A query with a partition key predicate skips entire [parts](ClickHouse%20Parts.md) without consulting the primary index at all.

- Partition by time period (`toYYYYMM(timestamp)`) is the most common pattern
- Effective only when queries consistently filter on the partition column
- Too many partitions (>1,000) creates metadata overhead and slows `INSERT`, `SELECT`, and DDL operations
- Partition pruning happens at the part level; primary key pruning happens at the granule level within surviving parts

**Combined effect:** partition pruning eliminates parts → primary key eliminates granules within remaining parts → ClickHouse reads only surviving granules.

### Data-skipping indexes (secondary indexes)

Applied after partition and primary key pruning, on surviving granules. Each index stores a summary of values in a block of granules (the `GRANULARITY` parameter controls how many granules per index block).

| Index type | Stores | Best for |
|---|---|---|
| `minmax` | min and max value | Low-cardinality numeric ranges (e.g., status codes, region IDs) |
| `set(N)` | up to N distinct values | Low-cardinality columns; set to 0 for unlimited |
| `bloom_filter` | probabilistic membership | High-cardinality equality filters (UUIDs, user IDs, log tokens) |
| `tokenbf_v1` | bloom filter of tokens | Full-text substring search (`LIKE`, `hasToken`) |
| `ngrambf_v1` | bloom filter of n-grams | Short substring search patterns |

**How skipping indexes work:** before reading granule data, ClickHouse checks the index for each surviving granule block. If the index proves the filter cannot match (e.g., the queried value is outside `minmax` range, or absent from the bloom filter), the entire block is skipped.

**Bloom filter false positives:** bloom filters can report a value as present when it isn't — a false positive. The granule block gets scanned unnecessarily, but no incorrect results are returned. Tune with `bloom_filter(false_positive_rate)`.

**Adding a skipping index:**
```sql
ALTER TABLE events
    ADD INDEX idx_user_id user_id TYPE bloom_filter(0.01) GRANULARITY 4;
ALTER TABLE events MATERIALIZE INDEX idx_user_id;
```

**When skipping indexes help:** when the indexed column has high correlation within granules — meaning matching values tend to cluster together on disk. If a user's events are spread randomly across all granules, a bloom filter index on `user_id` will show the value as present in nearly every block and skip nothing. Pre-sorting data by the target column (in primary key or a materialized view) dramatically improves skip effectiveness.

See [Bloom Filters](../../Algorithms/Bloom%20Filters.md)

### Projections

A projection is a hidden sub-table stored alongside the main table with a different sort order (and optionally a different set of aggregated columns). When a query matches a projection's sort key, ClickHouse transparently routes to it.

- Useful when you have two common query patterns that need different primary key orders
- Doubles write amplification and storage for the affected columns
- Prefer over duplicate materialized views when the access pattern is read-only re-sorting of existing data

## Key tradeoffs

- **Sparse index speed vs. granule scan overhead** — the primary index is fast but the minimum read unit is a granule (8,192 rows); point lookups always pay this granule tax
- **Partition count vs. pruning granularity** — finer partitions prune more aggressively but increase metadata overhead; there's a practical ceiling around 1,000 active partitions
- **Skipping index granularity vs. effectiveness** — smaller `GRANULARITY` means more index blocks and finer skipping, but higher index storage and maintenance cost; larger `GRANULARITY` is cheaper but skips less
- **Bloom filter false positive rate vs. index size** — lower false positive rate = larger bloom filter per block; 1%–5% is a common practical range
- **Column order lock-in** — changing the primary key requires a full table rewrite; choose carefully up front