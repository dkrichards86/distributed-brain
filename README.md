# Second Brain — Distributed Systems

A personal knowledge base for distributed systems concepts. Notes are plain markdown and can be read in any editor. Compatible with [Obsidian](https://obsidian.md) — open this directory as a vault if you want the graph view and navigation features — but Obsidian is not required.

## Directories

| Directory | What belongs here |
|---|---|
| `Algorithms/` | Data structures and algorithms — bloom filters, similarity measures, spatial indexing |
| `Databases/` | General database internals and concepts — storage engines, indexing, SQL, schema design |
| `Databases/ClickHouse/` | ClickHouse-specific architecture, indexing, and storage internals |
| `Databases/DynamoDB/` | DynamoDB-specific patterns, operations, and internals |
| `Engineering/` | Software engineering practices and runtime concepts — git, async models, auth, design principles, load management |
| `Observability/` | Logging, metrics, tracing, and reliability — the tools for understanding running systems |
| `Performance/` | Optimization patterns — caching, coalescing, benchmarking |
| `Distributed Systems/` | Distributed systems theory and protocols — consensus, leader election, distributed transactions, time and ordering |
| `Messaging/` | Messaging and streaming patterns — pub-sub, delivery semantics, backpressure |
| `Fault Tolerance/` | Failure patterns and resilience techniques — failure detection, circuit breakers, chaos engineering |
| `Architecture/` | Deployment and architectural patterns — sidecar, service mesh, service discovery |
| `Serialization & RPC/` | Serialization formats and RPC frameworks — Protocol Buffers, gRPC, Avro, Parquet, Thrift, Arrow, ORC, MessagePack |

When adding a new note, place it in the most fitting directory above. If no directory fits, create a new one and add it to this table.

## What's here

Notes on distributed computing topics. Each note follows a fixed structure — what the concept is, why it matters, how it works, and key tradeoffs.

## Note structure

```
# <concept>

<one-sentence definition>

## Why it matters
## How it works
## Key tradeoffs
```
