# Protocol Buffers (Protobuf)

A language-neutral binary serialization format developed by Google that uses a schema file (`.proto`) to define typed message structures, generating compact encodings and type-safe code for multiple languages.

## Why it matters

JSON and XML encode field names in every message, use text representations of numbers, and have no enforced schema. Protocol Buffers address all three: field names are replaced by compact integer tags on the wire, numbers use varint encoding (a 1-byte int fits in 1 byte, not 1 character), and the `.proto` schema is the enforced contract checked at compile time. The result is messages that are typically 3–10x smaller and 5–10x faster to serialize than JSON. Protobuf is the backbone of [gRPC](gRPC.md) and is widely used for persistent storage of structured data at Google and beyond.

## How it works

### Schema definition

Messages are defined in `.proto` files with typed fields and **field numbers**:

```protobuf
message Order {
  int64 id = 1;
  string customer_id = 2;
  repeated LineItem items = 3;
  OrderStatus status = 4;
}
```

The `protoc` compiler generates serialization/deserialization code. Field numbers, not names, identify fields on the wire.

### Wire format

Each field is encoded as a (field_number, wire_type, value) tuple:
- Fields with default values (0, false, empty string) are **omitted entirely** — absent fields decode to their default
- Varints pack small integers into 1–2 bytes using 7 bits per byte with a continuation bit
- Strings and bytes are length-prefixed

This means proto3 messages are intrinsically sparse: a message with 100 fields but only 5 set is small.

### Schema evolution

Field numbers are the schema contract. Safe changes:
- **Add a new field** with a new number — old clients ignore unknown fields; new clients use the default for missing fields
- **Remove a field** — mark the number as `reserved` so it's never reused

Breaking changes:
- **Renumber a field** — changes the wire representation; old and new clients disagree on meaning
- **Change a field type incompatibly** — changing `int32` to `string` breaks decoding

### proto2 vs. proto3

proto2 has `required` and `optional` keywords; proto3 removes `required` (all fields are implicitly optional) and adds `optional` back in proto3.15 as an explicit presence marker. Most new code uses proto3.

## Key tradeoffs

- **Not self-describing** — a protobuf blob without its schema is unreadable; you need the `.proto` file to interpret the bytes (unlike JSON or Avro with embedded schema)
- **Binary is not human-readable** — debugging requires proto-aware tools (`protoc --decode`, gRPC reflection, `protoscope`); logs that accidentally contain raw protobufs are unreadable
- **Build tooling required** — `protoc` and language-specific plugins must be integrated into the build pipeline; generated code must be kept in sync with `.proto` files
- **Field number discipline** — reassigning a field number is a silent breaking change; teams need process (code review, `reserved` enforcement) to prevent it

## Related concepts

- [gRPC](gRPC.md) — uses Protocol Buffers as its serialization layer; the `.proto` file defines both the message types and the service interface
- [Thrift](Thrift.md) — Facebook's equivalent; similar field-number-based binary encoding with pluggable protocols
- [Avro](Avro.md) — schema-registry-friendly alternative; schema embedded in data rather than compiled in; no code generation required
- [MessagePack](MessagePack.md) — binary alternative that doesn't require a schema; more flexible but no compile-time type safety
