# Snowflake ID

A 64-bit integer ID format — invented by Twitter, now widely adopted — that encodes a millisecond timestamp, worker identity, and per-millisecond sequence number to produce time-sortable IDs at high throughput without coordination.

## Why it matters

At Twitter's scale, a central ID generator is a bottleneck and single point of failure. Snowflake IDs let many worker nodes generate unique IDs independently while keeping them globally sortable by time — critical for feeds and timelines where insertion order matters.

## How it works

The 64-bit integer is partitioned into three fields:

| Bits  | Field | Notes |
|-------|-------|-------|
| 41    | Millisecond timestamp | Relative to a custom epoch; 41 bits gives ~69 years of range |
| 10    | Worker ID | Typically split as datacenter ID (5 bits) + machine ID (5 bits) = 1,024 workers |
| 12    | Sequence number | Up to 4,096 IDs per millisecond per worker; resets each millisecond |

Max throughput per worker: 4,096,000 IDs/second. With 1,024 workers: ~4 billion IDs/second cluster-wide.

IDs are strictly time-ordered within a single worker, and globally sortable by insertion time (to millisecond granularity) across workers — because the timestamp occupies the high bits. Sorting Snowflake IDs lexicographically is equivalent to sorting by creation time.

Requires each worker to have a unique ID assigned at startup. The worker assignment is typically done via ZooKeeper, a config file, or by claiming a slot in a shared registry.

Variants are used by Discord (with a different epoch and worker bit split), Instagram, Mastodon, and many others.

## Key tradeoffs

- **Compact** — 8 bytes vs. 16 bytes for a [UUID](UUID.md) or 12 bytes for an [ObjectID](ObjectID.md); significant at billions of rows
- **Time-sortable** — great for range queries and B-tree index locality; but also means IDs are predictable and reveal creation timestamps
- **Requires worker ID coordination** — nodes need unique worker IDs; if two workers share an ID, collisions are guaranteed. Reusing a worker ID after a restart within the same millisecond window is dangerous
- **Clock sensitivity** — if a worker's clock moves backward (NTP correction), the generator must pause until the clock catches up or risk generating a duplicate; compare to [Logical Clocks](Logical%20Clocks.md) which don't rely on physical time
- **69-year epoch limit** — the 41-bit timestamp overflows ~69 years from the chosen epoch; Twitter's epoch was 2010-11-04, which means overflow around 2079

## Related concepts

- [UUID](UUID.md) — 128-bit alternative; v7 UUIDs borrow Snowflake's time-prefix idea but sacrifice compactness
- [ObjectID](ObjectID.md) — MongoDB's 96-bit format; similar concept but second-level timestamp precision and no worker capacity limit
- [Logical Clocks](Logical%20Clocks.md) — Snowflake embeds a physical timestamp; hybrid logical clocks solve the clock-skew problem more rigorously
- [Partitioning and Sharding](../Databases/Partitioning%20and%20Sharding.md) — Snowflake IDs written in time order cause sequential writes to hit the same hash bucket or range partition; may need key salting to spread load
