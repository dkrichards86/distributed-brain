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
