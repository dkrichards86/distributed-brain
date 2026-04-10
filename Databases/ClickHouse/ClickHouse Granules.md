# ClickHouse Granules

The minimal selectable unit of data in [ClickHouse](ClickHouse%20Architecture.md) — a fixed block of consecutive rows (8,192 by default) that the primary index points into rather than indexing individual rows.

## Why it matters

Granules define the floor on how much data ClickHouse reads. Even a query matching a single row must read its entire granule. The entire indexing and skipping system — primary key, data-skipping indexes, partition pruning — exists to reduce how many granules get scanned. Understanding granules explains both why ClickHouse is fast for range queries and why it's slow for point lookups.

## How it works

Each [part](ClickHouse%20Parts.md) is divided into consecutive granules of `index_granularity` rows (default 8,192). ClickHouse stores one **index mark** per granule: the mark records the byte offset into the column files where that granule starts, plus the values of the primary key columns for the first row in the granule.

**Query execution:**
1. ClickHouse binary-searches the primary index marks to find the range of granules whose key range could contain matching rows.
2. It reads only those granules from disk (decompressing the column files at the marked byte offsets).
3. Within each granule, it filters rows by the full `WHERE` predicate.

Granules that fall entirely outside the primary key range are skipped without any I/O.

**Adaptive granularity:** ClickHouse also supports `index_granularity_bytes` (default 10 MB). When enabled, granule boundaries are placed at whichever comes first — 8,192 rows or 10 MB of data. This prevents very wide rows from producing enormous granules.

**[Data-skipping indexes](ClickHouse%20Indexing%20Strategies.md) operate at granule-block granularity:** secondary indexes summarize a configurable number of granules (the `GRANULARITY` parameter on the index definition). They are evaluated after the primary index has already eliminated granule ranges.

## Key tradeoffs

- **Scan floor** — every read pays for at least one full granule; point lookups by non-primary-key columns are expensive relative to the data actually needed
- **Compression** — larger granules compress better (more data per block) but increase the minimum read size
- **Index size** — one mark per granule keeps the primary index small enough to fit in memory; per-row indexing would be faster for point lookups but prohibitively large
- **Tuning** — smaller `index_granularity` means finer-grained skipping but a proportionally larger index; the default of 8,192 is appropriate for most workloads
