# Key-Value Databases

Store data as key → value pairs where the database treats values as opaque blobs and access is limited to key lookups.

## Why it matters

When access patterns are predictable and speed matters more than queryability, key-value stores eliminate the overhead of schema validation, query planning, and join execution. They scale horizontally with minimal coordination because data is partitioned by key.

## How it works

Each entry is a (key, value) pair. The database makes no assumptions about value structure. Access is via exact key lookup, range scans on ordered keys, or atomic operations (increment, compare-and-swap). Data is often stored in memory (Redis) or on SSD with [LSM trees](LSM%20Trees.md) ([DynamoDB](DynamoDB/DynamoDB%20Query%20Patterns.md)). Partitioning by key hash makes horizontal scaling straightforward.

## Key tradeoffs

- No complex queries — you cannot filter or aggregate on value contents without fetching everything
- No relationships between items — cross-key joins don't exist
- Poor fit for analytical or exploratory workloads where access patterns aren't known ahead of time
- **Examples:** DynamoDB, Redis
