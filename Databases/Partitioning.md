# Partitioning

Dividing a table's data into smaller, independently managed pieces — either by rows (horizontal) or by columns (vertical) — within a single database instance.

## Why it matters

Large tables degrade query performance over time: indexes grow fat, vacuums slow down, and range scans read far more data than they need. Partitioning lets the database prune irrelevant chunks at the storage layer before executing a query, and allows old partitions to be dropped instantly (a metadata operation) rather than deleted row-by-row.

## How it works

### Horizontal partitioning (range, list, hash)

Rows are split across multiple physical sub-tables based on a partition key:

- **Range** — rows with key values in a given range belong to the same partition (e.g., one partition per month of `created_at`). Postgres, MySQL, and most SQL databases support this natively. Enables partition pruning for range queries and fast partition drops for time-series retention.
- **List** — rows are assigned to a partition based on a discrete set of values (e.g., `region IN ('us-east', 'eu-west')`). Good for multi-tenant or regional data.
- **Hash** — `hash(key) % N` assigns rows to partitions. Distributes uniformly but sacrifices range pruning.

The database routes queries to the right partition automatically. With pruning enabled, `WHERE created_at > '2024-01-01'` only scans the matching partitions.

### Vertical partitioning

Columns are split across multiple tables sharing the same primary key. Wide tables with infrequently accessed columns (large blobs, audit fields) are split so hot queries don't read cold columns.

Postgres doesn't do this natively; it's implemented by the schema designer via table normalization or explicit column-group tables.

### Sub-partitioning

A partition can itself be partitioned by a second key (e.g., range by month, then hash by user ID). Adds pruning granularity at the cost of management complexity.

## Key tradeoffs

- **Partition pruning dependency** — pruning only works if the query filter includes the partition key; queries without it scatter across all partitions and are slower than an unpartitioned table with a good index
- **Partition maintenance overhead** — future partitions must be created in advance (or automated); missing a range partition causes inserts to fail or fall into a default catch-all partition
- **Cross-partition queries** — joins and aggregations that span all partitions may be slower than on an unpartitioned table if the planner can't prune
- **Partition key immutability** — updating a row's partition key value triggers a delete-and-insert across partitions, which is expensive and can break foreign keys

## Related concepts

- [Sharding](Sharding.md) — sharding is horizontal partitioning taken across multiple nodes; partitioning stays within one instance
- [Federation](Federation.md) — federation splits by entity type across instances (different schemas per node), orthogonal to row-level partitioning
- [Write-Ahead Logging](Write-Ahead%20Logging.md) — each partition has its own storage files but shares the instance WAL
- [Indexes](Indexes.md) — indexes on a partitioned table are themselves partitioned; a global index spanning all partitions is unusual and expensive to maintain
