# Parquet

A columnar storage file format designed for efficient analytical queries on large datasets, storing data organized by column rather than by row to maximize compression and minimize I/O for aggregate workloads.

## Why it matters

Analytics queries (e.g., `SELECT AVG(revenue), region FROM orders GROUP BY region`) only need a few columns out of potentially hundreds. A row-oriented format (CSV, JSON, Avro) must read the entire row to extract one attribute. Parquet stores all values for a single column together, so a query that needs two columns from a 200-column table reads roughly 1% of the data. Combined with column-level compression and predicate pushdown, Parquet can reduce query I/O by orders of magnitude. It's the de facto standard format for data lakes (S3, GCS, ADLS) and is supported natively by Spark, Snowflake, BigQuery, Athena, DuckDB, ClickHouse, and Pandas.

## How it works

### Physical layout

Data is organized in three levels:

1. **Row group** (~128MB default) — a horizontal partition of the dataset; contains data for every column
2. **Column chunk** — all values for one column within a row group; stored contiguously
3. **Page** (~1MB default) — the unit of compression and encoding within a column chunk

The file footer contains the schema and statistics (min, max, null count, distinct count) for every column chunk and page. Readers parse the footer first to determine which row groups and pages are relevant before reading any data.

### Predicate pushdown

If a query filters `WHERE ts > '2024-01-01'`, the reader checks the `ts` column chunk's min/max statistics in the footer. Row groups where max(ts) ≤ the threshold are skipped entirely without reading a byte of data. Bloom filters (optional) enable point-lookup skipping.

### Encoding

Each column uses the encoding best suited to its data distribution:
- **Dictionary encoding** — for low-cardinality columns (e.g., `status`, `country`); values replaced by integer IDs
- **Run-length encoding (RLE)** — for repeated values; stores (value, count) pairs
- **Delta encoding** — for monotonically increasing columns (timestamps, IDs)
- **Bit packing** — compresses small integers

Compression codecs (Snappy, Zstd, LZ4, Gzip) are applied on top of encoding per page.

### Nested data

Parquet supports deeply nested schemas (structs, arrays, maps) using Dremel's repetition/definition level encoding. This allows storing semi-structured data (e.g., JSON-like records) in columnar form without flattening.

## Key tradeoffs

- **Write amplification for small writes** — row groups must be complete to benefit from column statistics; writing many small files (the "small files problem") destroys read performance; compaction is required
- **No in-place updates** — Parquet files are immutable; updating a record requires rewriting the entire row group; Delta Lake and Apache Iceberg add a transaction log on top of Parquet to handle updates and deletes
- **Slow for point lookups** — retrieving a single row requires reading one page from every column; row-oriented formats are better for primary-key lookups
- **Footer I/O for small files** — reading the footer is always required; for files with few row groups, footer overhead is disproportionate

## Related concepts

- [Avro](Avro.md) — complementary row-oriented format; typical pipeline pattern is to ingest data as Avro (streaming) and persist to Parquet (analytics)
- [ORC](ORC.md) — columnar format from the Hive ecosystem; functionally similar to Parquet but with tighter Hive/Spark integration and native ACID support
- [Apache Arrow](Apache%20Arrow.md) — in-memory columnar format; Parquet files are efficiently decoded directly into Arrow buffers, enabling zero-copy pipelines
- [Columnar Databases](../Databases/Columnar%20Databases.md) — Parquet applies the same columnar storage principle to file format; databases like ClickHouse use a similar on-disk layout internally
- [ClickHouse Architecture](../Databases/ClickHouse/ClickHouse%20Architecture.md) — ClickHouse can read and write Parquet files natively; its internal storage format is conceptually similar
