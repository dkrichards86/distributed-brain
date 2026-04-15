# Thrift

Apache Thrift is a cross-language RPC framework and binary serialization system originally developed at Facebook, combining a schema definition language, pluggable wire protocols, and a transport layer.

## Why it matters

Thrift predates gRPC and protobuf's open-source releases and was the dominant RPC framework at large-scale internet companies (Facebook, Twitter, Evernote). It remains in heavy use in systems built before gRPC matured — Cassandra uses Thrift for its original client protocol, and many internal Facebook/Meta services still rely on it. Understanding Thrift is important when working with any of those systems, and its design reflects lessons about cross-language RPC that later influenced gRPC.

## How it works

Services and data types are defined in `.thrift` IDL files. The Thrift compiler generates client and server code for the target language. The stack has three independently configurable layers:

### Protocols (serialization format)

- **BinaryProtocol** — simple binary encoding; fast, compact, but no backward-compatible schema evolution
- **CompactProtocol** — variable-length integer encoding; smaller than Binary for numeric-heavy payloads
- **JSONProtocol** — human-readable but larger; useful for debugging

### Transports

- **TFramedTransport** — frames messages with a length prefix; required for non-blocking servers
- **TBufferedTransport** — buffers I/O for throughput
- **THttpTransport** — sends Thrift over HTTP; works with standard HTTP infrastructure

### Servers

- **TSimpleServer** — single-threaded; fine for testing
- **TThreadPoolServer** — one thread per connection
- **TNonblockingServer** — event-driven with a thread pool; highest throughput

Schema evolution: fields are identified by integer field IDs (like protobuf). Adding a new optional field with a new ID is backward-compatible. Removing a field requires the ID to be reserved. The required/optional distinction is weaker than in protobuf — `required` fields in Thrift are effectively optional in practice, and the community discourages using `required`.

## Key tradeoffs

- **Ecosystem momentum has shifted to gRPC** — most new tooling, cloud-native integrations, and community investment is around gRPC/protobuf; Thrift is in maintenance mode for most use cases
- **More protocol/transport flexibility** — both a strength (fits more environments) and a weakness (more configuration surface, harder to standardize across a large org)
- **No native HTTP/2 or streaming** — Thrift predates HTTP/2; streaming requires building on top of the basic RPC model; gRPC's native streaming support is more ergonomic
- **Weaker schema evolution guarantees** — Thrift's type system has sharp edges around required/optional that have caused production bugs; protobuf's proto3 removed required fields entirely

## Related concepts

- [gRPC](gRPC.md) — the modern successor for most new service-to-service RPC; uses Protocol Buffers for serialization and HTTP/2 for transport
- [Protocol Buffers](Protocol%20Buffers.md) — Google's serialization format; serves the same role as Thrift's BinaryProtocol/CompactProtocol but with better tooling and ecosystem
- [Avro](Avro.md) — another Apache serialization format; schema-registry-friendly, row-oriented, used heavily in the Kafka ecosystem
