# Relational Databases

Store data in tables with predefined schemas, connected via foreign keys, and queried with SQL.

## Why it matters

Most applications need to store related entities and query across them with strong correctness guarantees. Relational databases provide ACID transactions and a flexible query layer (SQL) so you can ask arbitrary questions of your data without designing access patterns upfront.

## How it works

Data lives in tables — rows are records, columns are typed attributes. Tables reference each other via foreign keys. The query engine parses SQL, builds an execution plan, and uses [[B-Trees|indexes]] to minimize the data it reads. Transactions use write-ahead logging and locking (or MVCC) to guarantee atomicity, consistency, isolation, and durability.

## Key tradeoffs

- Rigid schemas make structural changes painful — adding or removing columns on large tables can require expensive migrations
- Horizontal scaling for high-write workloads is hard; most relational databases scale vertically or via read replicas
- Performance degrades on very large datasets without careful indexing and partitioning
- SQL schema design: [[SQL Normalization]], [[SQL Joins]]
- **Examples:** PostgreSQL, MySQL, SQLite
