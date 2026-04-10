# ClickHouse Architecture

A [column-oriented](../Columnar%20Databases.md) analytical database that achieves high query performance by storing data per-column, using immutable writes, and organizing data in a partition → part → granule hierarchy.

## Why it matters

When you need to run aggregations over billions of rows, ClickHouse is remarkably fast — but only for the right workloads. Its architecture is a set of deliberate trade-offs that make analytical queries blazing fast while making row-level access, frequent updates, and low-volume inserts slow or operationally painful. Understanding the internals tells you both when to reach for it and how to use it correctly.

## How it works

### Column-oriented storage

Each column is stored in a separate file on disk. A query that needs 3 out of 50 columns reads only those 3 column files. For analytical queries that aggregate across millions of rows on specific attributes, this means dramatically less I/O than row-oriented storage, plus better compression (homogeneous data compresses better).

Trade-off: reconstructing full rows requires reading multiple column files — row-level access is slow.

### Immutable writes

ClickHouse never modifies data in place. Every INSERT creates new storage. Updates and deletes are implemented as asynchronous mutations that mark records for exclusion; physical removal happens during background merging.

This enables high write throughput (no locking or coordination) but makes frequent updates expensive and individual row modifications operationally awkward.

### The hierarchy: Partitions → Parts → Granules

Data is organized into [ClickHouse Partitions](ClickHouse%20Partitions.md) (logical time-based groupings) → [ClickHouse Parts](ClickHouse%20Parts.md) (physical storage units created per INSERT, consolidated by background merging) → [ClickHouse Granules](ClickHouse%20Granules.md) (the minimal 8,192-row selectable unit that the primary index points into).

### Primary keys work differently

ClickHouse primary keys don't enforce uniqueness — they determine **sort order** within parts and which granules to scan.

- **First column:** binary search on the primary index — O(log n)
- **Subsequent columns:** linear scan of the index marks — O(n)

Column order matters significantly. Put the most selective filter column first. Limit primary keys to 3–4 columns — each additional column increases index size and scan cost.

### When ClickHouse is the wrong tool

| Pattern | Why it's problematic |
|---|---|
| Row-level access by ID | Must scan granules; no efficient single-row lookup |
| Frequent updates | Each mutation impacts all data in affected granules; async, expensive |
| Low-volume inserts | Each INSERT creates a new part; thousands of tiny parts degrade queries |
| Transactional workloads | No ACID guarantees; not designed for operational data patterns |

## Key tradeoffs

- **Columnar read speed vs. write flexibility** — columnar storage is fast for analytics but forces batch-oriented writes and makes updates painful
- **Immutability vs. correctness** — immutable writes enable high throughput but mean "deleted" data is still readable until the next merge; not suitable for compliance-sensitive data that must be purged immediately
- **Part count vs. query latency** — more parts = more scan overhead per query; tuning insert batch size directly impacts query performance
- **Partition granularity** — finer partitions (daily) allow better pruning for time-range queries but increase partition count overhead; coarser partitions (monthly) reduce overhead but require scanning more data
- **Primary key column order** — binary search only applies to the first column; getting this wrong means paying linear costs on high-cardinality filters

## Related concepts

- [LSM Trees](../LSM%20Trees.md) — ClickHouse's MergeTree shares LSM concepts (immutable writes, background merging, deferred deletes) but is column-oriented and skips the in-memory MemTable buffer; Parts are the SSTable analog

