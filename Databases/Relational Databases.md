# Relational Databases

Store data in tables with predefined schemas, connected via foreign keys, and queried with SQL.

## Why it matters

Most applications need to store related entities and query across them with strong correctness guarantees. Relational databases provide ACID transactions and a flexible query layer (SQL) so you can ask arbitrary questions of your data without designing access patterns upfront.

## How it works

Data lives in tables — rows are records, columns are typed attributes. Tables reference each other via foreign keys. The query engine parses SQL, builds an execution plan, and uses [indexes](B-Trees.md) to minimize the data it reads. Transactions use [write-ahead logging](Write-Ahead%20Logging.md) and locking (or [MVCC](MVCC.md)) to guarantee atomicity, consistency, isolation, and durability.

## Key tradeoffs

- Rigid schemas make structural changes painful — adding or removing columns on large tables can require expensive migrations
- Horizontal scaling for high-write workloads is hard; most relational databases scale vertically or via [read replicas](Replication.md)
- Performance degrades on very large datasets without careful indexing and partitioning
- SQL schema design: [SQL Normalization](SQL%20Normalization.md), [SQL Joins](SQL%20Joins.md)
- **Examples:** PostgreSQL, MySQL, SQLite
