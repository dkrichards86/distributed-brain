# Avro

A row-oriented binary serialization format from the Apache Hadoop ecosystem that embeds the schema alongside the data, enabling schema evolution without code generation and making it the dominant serialization format in Kafka-based pipelines.

## Why it matters

Streaming pipelines need a compact binary format where producers and consumers can evolve independently — new fields added by producers shouldn't break existing consumers. Avro solves this with dynamic schema resolution: the writer's schema is stored with the data (in a file header or looked up from a schema registry), and the Avro runtime reconciles it with the reader's schema at read time, applying defaults for missing fields and ignoring unknown fields. This makes Avro the standard format for Kafka with a schema registry.

## How it works

Schemas are written in JSON and describe records, enums, arrays, maps, unions, and primitives. There is no code generation step — encoding and decoding can be done dynamically at runtime using just the schema.

### Data files

Avro Object Container Files (`.avro`) embed the writer's schema in the file header. Any reader can decode the file without needing out-of-band schema information.

### Schema registry (Kafka integration)

In Kafka pipelines, embedding the full schema in every message is wasteful. Instead:

1. Producers register their schema with a schema registry (Confluent Schema Registry is the standard)
2. Each Kafka message starts with a magic byte and a 4-byte schema ID
3. Consumers look up the schema by ID from the registry and decode the payload

Schema compatibility rules (backward, forward, full) are enforced at registration time:
- **Backward compatible** — new schema can read data written by old schema (add fields with defaults)
- **Forward compatible** — old schema can read data written by new schema (only remove fields with defaults)
- **Full** — both directions

### Wire format

No field names on the wire — values are encoded in schema-defined order, with each primitive using its natural binary encoding (zigzag encoding for integers). Null is allowed anywhere via unions (`["null", "string"]` is the standard nullable field pattern).

## Key tradeoffs

- **Schema registry dependency** — in Kafka setups, the schema registry is a critical component; if it's unavailable, new consumers can't start; schema ID conflicts cause decoding failures
- **Row-oriented** — not suitable for analytical scans; if you need column projection, use [Parquet](Parquet.md) or [ORC](ORC.md)
- **Dynamic typing option** — you can encode and decode Avro without generating code (just pass the schema as a string), but generated code has better performance and catches schema mismatches at compile time
- **JSON schema syntax** is verbose for complex nested types; Thrift/protobuf IDLs are more readable for service definitions

## Related concepts

- [Parquet](Parquet.md) — complementary to Avro; Avro is row-oriented and used for streaming/transport, Parquet is columnar and used for analytical storage; pipelines often ingest as Avro and store as Parquet
- [Thrift](Thrift.md) — another Apache serialization format; RPC-focused rather than data-pipeline-focused
- [Protocol Buffers](Protocol%20Buffers.md) — Google's serialization format; stronger schema evolution tooling than Avro but no dynamic typing
- [Pub-Sub Patterns](../Messaging/Pub-Sub%20Patterns.md) — Avro is the dominant serialization format for Kafka messages; the schema registry ties schema lifecycle to topic lifecycle
