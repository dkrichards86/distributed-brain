# Columnar Databases

Store data by column rather than by row — all values for a single attribute are co-located on disk, enabling fast scans and high compression.

## Why it matters

Analytical queries typically read a few columns across millions of rows. Row-oriented stores must read entire rows to get one attribute. Columnar storage lets queries skip irrelevant columns entirely, and groups similar values together for aggressive compression — dramatically reducing I/O for aggregate workloads.

## How it works

Instead of storing row1(col1, col2, col3), row2(col1, col2, col3)... data is stored as col1(row1, row2...), col2(row1, row2...)... On a query like `SELECT AVG(price) FROM orders`, only the `price` column is read from disk. Adjacent values in a column are often similar, so run-length encoding and dictionary encoding achieve high compression ratios. Vectorized execution processes batches of column values at once.

## Key tradeoffs

- Slow for individual record lookups — fetching a single row requires reading from many column files
- Poor fit for transactional or frequently-updated data — in-place updates are expensive; most columnar stores are append-oriented
- **Examples:** [ClickHouse](ClickHouse/ClickHouse%20Architecture.md)

## Related concepts

- [Parquet](../Serialization%20%26%20RPC/Parquet.md) — a columnar file format for data lakes; applies the same column-per-file principle to portable storage on object stores
- [ORC](../Serialization%20%26%20RPC/ORC.md) — another columnar file format from the Hive ecosystem; similar to Parquet with tighter Hive ACID integration
- [Apache Arrow](../Serialization%20%26%20RPC/Apache%20Arrow.md) — a columnar in-memory format; the in-process complement to Parquet on disk; many columnar databases use Arrow as their internal representation
