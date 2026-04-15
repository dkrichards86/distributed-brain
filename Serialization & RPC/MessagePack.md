# MessagePack

A compact binary serialization format that encodes JSON-compatible data structures (objects, arrays, strings, numbers, booleans, null) more efficiently than JSON, with no schema required.

## Why it matters

JSON is the universal language of APIs, but it's verbose: field names are repeated in every message, numbers are encoded as ASCII digits, and booleans are 4–5 characters. MessagePack is a binary drop-in replacement that preserves JSON's schema-less, dynamic nature while reducing payload size by ~30–50% and parsing time significantly. It's a practical choice when you want the flexibility of JSON but the performance of a binary format, without the overhead of managing `.proto` or `.thrift` schemas.

## How it works

MessagePack maps directly to JSON types: nil, bool, int, float, str, bin (raw bytes), array, map, and extension types (for timestamps, custom types).

Each value is encoded as a type tag followed by the value:
- Small integers (-32 to 127) fit in a single byte — no type prefix needed
- Strings and arrays under 32/16 elements use a compact 1-byte header
- Larger values use 2- or 4-byte headers with explicit lengths
- Maps encode key-value pairs sequentially (same as JSON objects, but binary keys/values)

There is no schema definition language or code generation step. Any language with a MessagePack library can encode/decode any value. Dynamic decoding produces native maps and arrays; no struct binding required.

**Extension types** allow custom data types with a type code and raw bytes, enabling timestamps, decimals, or application-specific types without breaking general parsers.

## Key tradeoffs

- **No schema, no compile-time safety** — field renames and type changes go undetected until runtime; without a schema registry or versioning discipline, API evolution is fragile
- **Still key-per-message** — unlike [Protocol Buffers](Protocol%20Buffers.md) or [Thrift](Thrift.md), field names (as strings) are repeated in every message; the advantage over JSON is binary encoding of the names and values, not their elimination
- **Marginal advantage in practice** — JSON parsing is heavily optimized (simdjson parses at memory bandwidth speeds); for many workloads the performance gap between JSON and MessagePack is smaller than expected
- **Tooling gap** — JSON has ubiquitous tooling (browser devtools, `jq`, `curl`); MessagePack messages require specific decoders; debugging and logging are harder
- **No streaming/RPC layer** — MessagePack is purely a serialization format; you need to build or choose a transport and framing layer (unlike gRPC, which is a full framework)

## Related concepts

- [Protocol Buffers](Protocol%20Buffers.md) — schema-based alternative; smaller messages (no field names on wire), compile-time type safety, better for long-lived APIs
- [Avro](Avro.md) — schema-based alternative with dynamic typing option; better for schema evolution in streaming pipelines
- [Thrift](Thrift.md) — full RPC framework with schema; like Protocol Buffers, eliminates field names from the wire format
