# DynamoDB Query Patterns

A set of data modeling strategies for designing efficient access patterns in Amazon DynamoDB's key-value store.

## Why it matters

Relational databases let you query any column after the fact. DynamoDB requires you to know your access patterns upfront — a mismatched model causes full scans, runaway costs, or throttling. Getting the patterns right is the difference between a fast, cheap table and an unusable one.

## How it works

DynamoDB routes items to partitions via a **partition key (PK)**. An optional **sort key (SK)** enables range queries within a partition. All other attributes are opaque to the query engine unless indexed.

**Core query patterns:**

| Pattern | Mechanism |
|---|---|
| **Point lookup** | Query on PK alone — O(1), single partition |
| **Range query** | PK + SK condition (`begins_with`, `between`, `>`, `<`) |
| **Single-table design** | Multiple entity types in one table; overload PK/SK with prefixes (e.g. `PK=USER#123`, `SK=ORDER#456`) |
| **Hierarchical / prefix** | SK encodes hierarchy (`SK=REGION#us-east#AZ#use1-az1`) — query a prefix to get all children |
| **One-to-many** | All child items share the same PK, differentiated by SK |
| **Many-to-many (adjacency list)** | Store both directions as separate items — `PK=A, SK=B` and `PK=B, SK=A` |
| **Time-series** | SK as ISO timestamp; range query for time windows |
| **GSI overloading** | Reuse GSI PK/SK across entity types to handle multiple access patterns with one index |
| **Sparse GSI** | Attribute only present on some items; GSI only indexes those items — acts as a filtered view |
| **Write sharding** | Append random suffix to hot PK (`USER#123#3`) to spread writes across partitions; fan-out on read |

See [[DynamoDB Operation Semantics]]

**Secondary indexes:**
See [[DynamoDB Indexes]]

## Key tradeoffs

- **Denormalization vs. storage cost** — single-table design duplicates data to serve multiple access patterns; storage is cheap but updates must touch multiple items
- **GSI cost** — each GSI replicates data and has its own write capacity; more indexes = higher cost
- **Sparse GSI efficiency** — great for filtered queries, but you lose items that don't have the attribute (intentional or accidental)
- **Write sharding complexity** — solves [[DynamoDB Hot Partitions|hot partition]] throttling but requires scatter-gather reads (query all shards, merge results)
- **No ad hoc queries** — any unplanned access pattern requires a new index or a full scan; scan is expensive and slow

**Hard limits:** 400KB per item, 1MB per query response, 10GB per partition key value.

