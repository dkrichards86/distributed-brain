# Analytical Databases

Optimized for complex aggregations, time-series analysis, and multi-dimensional operations over large historical datasets — also called data warehouses.

## Why it matters

Operational databases are tuned for fast individual record access. Analytical workloads are fundamentally different: scan billions of rows, compute aggregates across multiple dimensions, join large tables. Analytical databases are purpose-built for these query shapes, often enabling queries in seconds that would take hours on a transactional store.

## How it works

Typically use [columnar storage](Columnar%20Databases.md) internally to minimize I/O on wide tables. Queries are compiled and parallelized across many nodes. Pre-computed materialized views and aggregations speed up common query patterns. Data is usually loaded in bulk (ETL/ELT pipelines) rather than inserted row by row. Query planners are tuned for full-table scans and hash joins rather than index lookups.

## Key tradeoffs

- High latency for small transactional queries — not a substitute for an operational database
- Poor at individual record updates — data is often append-only or batch-replaced
- Real-time ingestion is complex — most warehouses favor batch loads over streaming inserts
- **Examples:** Redshift, Snowflake
