# ORC (Optimized Row Columnar)

A columnar storage file format from the Apache Hive ecosystem designed for high compression ratios and fast analytical reads, with built-in support for ACID transactions within Hive.

## Why it matters

Before ORC, Hive used RCFile — technically column-oriented but with poor compression and no predicate pushdown. ORC introduced stripe-level statistics, lightweight indexes, and bloom filters, cutting I/O dramatically for analytical queries in the Hadoop ecosystem. It's the native format for Hive ACID tables (insert/update/delete with snapshot isolation) and remains the preferred format in environments tightly coupled to Hive and Spark on YARN.

## How it works

### Physical layout

Data is organized in **stripes** (~256MB default), each containing:
- **Index data** — row group indexes with min/max statistics every 10,000 rows; bloom filter indexes for columns where bloom filters are enabled
- **Data** — column data for each column in the stripe, encoded and compressed
- **Stripe footer** — column statistics (min, max, sum, count) for the entire stripe

The **file footer** contains the schema, stripe locations, column statistics for the whole file, and optional user metadata. The **postscript** at the very end of the file records the compression codec and footer length.

### Predicate pushdown

Three levels of skip:
1. **File-level** statistics in the footer — skip the entire file if stats don't match the predicate
2. **Stripe-level** statistics — skip stripes where column stats exclude the predicate value
3. **Row-group-level** indexes — skip 10,000-row groups within a stripe

Bloom filters (optional, per column) allow point-lookup skipping within row groups for equality predicates.

### Encoding

- **Run-length encoding v2** — used for integers and timestamps; handles 4 sub-encodings (short repeat, direct, patched base, delta) chosen per block
- **Dictionary encoding** — for string columns with low cardinality
- Compression codecs: Zlib, Snappy, LZ4, Zstd applied per stripe

### ACID support

Hive's ACID implementation stores base files and delta files in ORC format. Compaction merges deltas back into base files. This is the main reason to prefer ORC over [Parquet](Parquet.md) when using Hive with insert/update/delete operations.

## Key tradeoffs

- **Narrower ecosystem than Parquet** — Parquet has won the data lake interoperability battle; Snowflake, BigQuery, Redshift, and most data lake tooling prefer Parquet; ORC support is less universal
- **Better native ACID in Hive** — if you're using Hive with transactional tables (updates and deletes), ORC is the required format; Parquet-based ACID (via Delta Lake or Iceberg) is more complex to set up in Hive
- **Similar query performance to Parquet** — benchmarks show ORC and Parquet within ~10–20% of each other for typical analytical queries; neither has a decisive performance advantage
- **Stripe statistics vs. row-group statistics** — ORC's 10,000-row row-group index is finer-grained than Parquet's page-level stats, potentially enabling more precise predicate pushdown; in practice the difference is workload-dependent

## Related concepts

- [Parquet](Parquet.md) — the dominant alternative; functionally similar but with broader ecosystem support; choose Parquet for data lake interoperability, ORC for Hive ACID
- [Columnar Databases](../Databases/Columnar%20Databases.md) — ORC and Parquet apply the columnar storage principle to file formats; database engines like ClickHouse use similar layouts internally
- [Avro](Avro.md) — row-oriented format from the same Apache ecosystem; used for streaming/transport where ORC/Parquet are used for storage
