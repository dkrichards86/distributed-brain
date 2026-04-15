# Apache Arrow

An in-memory columnar data format and cross-language runtime that defines a shared memory layout for columnar data, enabling zero-copy data exchange between different runtimes and systems.

## Why it matters

Data pipelines typically serialize data at every boundary: a Spark executor serializes to Parquet, sends bytes over the wire, and the receiver deserializes back to its own in-memory representation. If both sides speak Arrow, they share the same memory layout — exchanging data is a pointer pass, not a serialize/copy/deserialize cycle. This eliminates a major bottleneck in multi-engine analytics pipelines (Python pandas ↔ R ↔ C++ DuckDB ↔ Java Spark) and in single-process pipelines where data moves between libraries.

## How it works

### In-memory format

Arrow defines a columnar memory layout:
- Each column is a **contiguous buffer** of values in a fixed-width or variable-length encoding
- A separate **validity bitmap** encodes nulls (1 bit per value) — no sentinel values
- Nested types (lists, structs, maps) use offset buffers that index into child arrays
- The layout is defined precisely enough that a C++ process and a Python process can point at the same memory without copying

This canonical layout is the key: because every Arrow implementation agrees on byte ordering and alignment, interop is zero-copy.

### IPC format

For cross-process exchange, Arrow defines a streaming IPC format: a sequence of record batches (chunks of ~64K rows), each preceded by a metadata message describing the schema. The payload itself is the same in-memory layout, ready to use without deserialization.

### Arrow Flight

A gRPC-based RPC protocol for bulk Arrow data transfer across a network. A Flight server exposes endpoints for reading (DoGet) and writing (DoPut) datasets. Internally, it streams Arrow IPC record batches over [gRPC](gRPC.md) bidirectional streams, achieving throughput close to the network limit for columnar data.

### Parquet integration

[Parquet](Parquet.md) files can be decoded directly into Arrow buffers by the `parquet-cpp` / `pyarrow` reader — the column chunks map naturally to Arrow arrays. This makes Parquet+Arrow the standard on-disk and in-memory pair for analytical data: store as Parquet (compressed, durable), process as Arrow (fast, zero-copy).

## Key tradeoffs

- **In-memory format, not a storage format** — Arrow is for RAM; Parquet is for disk; they're complementary, not competing
- **Memory must be materialized** — unlike lazy streaming formats, Arrow record batches are fully materialized arrays; processing very large datasets requires chunking (streaming record batches)
- **Cross-process zero-copy requires shared memory** — zero-copy exchange works within a process or via POSIX shared memory; across machines, data still travels over the network (Arrow Flight), though deserialization cost is eliminated
- **Layout is rigid** — the fixed in-memory layout enables interop but limits optimization for specific access patterns (e.g., a database engine might use a different internal layout for better cache behavior)

## Related concepts

- [Parquet](Parquet.md) — columnar on-disk format; Arrow is the in-memory complement; pyarrow reads Parquet directly into Arrow without an intermediate representation
- [gRPC](gRPC.md) — Arrow Flight is built on gRPC; understanding gRPC streaming is prerequisite to understanding Flight's performance characteristics
- [Columnar Databases](../Databases/Columnar%20Databases.md) — the same columnar principle applied to persistent storage; many columnar databases (DuckDB, ClickHouse) use Arrow as their in-memory representation
