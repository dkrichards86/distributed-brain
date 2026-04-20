# UUID (Universally Unique Identifier)

A 128-bit identifier designed to be unique across space and time without central coordination. Microsoft's equivalent term, **GUID (Globally Unique Identifier)**, refers to the same format and standard (RFC 4122).

## Why it matters

Distributed systems need to generate unique IDs without a central authority that would become a bottleneck or single point of failure. UUIDs let any node generate an ID independently with negligible collision probability.

## How it works

Represented as 32 hex characters in 5 groups separated by hyphens: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`. Several versions exist:

- **v1** — combines MAC address + timestamp. Unique but leaks node identity and not random; timestamp is fine-grained but stored in a scrambled byte order that breaks lexicographic sorting.
- **v4** — 122 bits of cryptographic randomness (6 bits reserved for version/variant). The most common variant. No structure, no coordination, extremely low collision probability.
- **v6 / v7** — newer (RFC 9562, 2024). v7 uses a Unix millisecond timestamp in the high bits, making UUIDs time-sortable while retaining randomness in the low bits. Significantly better for database primary keys than v4.

The "universally unique" claim relies on randomness: the probability of a v4 collision across 1 billion UUIDs per second for 85 years is about 50%.

## Key tradeoffs

- **v4 randomness vs. index locality** — random UUIDs scatter writes across a B-tree index, causing page splits and poor cache behavior; v7 solves this by prefixing with a sortable timestamp
- **Size** — 128 bits (16 bytes) vs. 64-bit alternatives like [Snowflake IDs](Snowflake%20ID.md); matters at scale when stored as a primary key across billions of rows
- **No coordination needed** — but also no global ordering guarantee; you can't determine which UUID was generated first unless using v7
- **Hot partition avoidance** — v4's randomness distributes keys uniformly across hash shards (see [Sharding](../Databases/Sharding.md)), but means range scans are useless

## Related concepts

- [Snowflake ID](Snowflake%20ID.md) — a compact 64-bit time-sortable alternative with embedded machine identity
- [ObjectID](ObjectID.md) — MongoDB's 96-bit ID format, also timestamp-prefixed
- [Sharding](../Databases/Sharding.md) — ID format directly affects whether writes hot-spot on a single shard
- [Logical Clocks](Logical%20Clocks.md) — v7 UUIDs use physical timestamps in the high bits, trading true causal ordering for practical sortability
