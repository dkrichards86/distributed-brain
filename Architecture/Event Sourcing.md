# Event Sourcing

A persistence pattern where state changes are stored as an immutable, append-only log of events rather than as the current state.

## Why it matters

Storing only current state loses history. Event sourcing preserves a complete audit trail and makes it possible to reconstruct state at any point in time, replay events into new projections, or replicate changes to downstream systems without additional instrumentation. The log becomes the single source of truth.

## How it works

Every mutation is captured as a named, timestamped event (`OrderPlaced`, `PaymentProcessed`, `ItemShipped`) and appended to an event store. No records are updated in place — the log is append-only.

Current state is derived by replaying the event log from the beginning (or from a **snapshot** — a periodically saved checkpoint of current state that bounds replay time). Consumers tail the event log to build their own read-optimized projections; different consumers can build different views of the same events.

This is often combined with [CQRS](CQRS.md): the event log is the write model; projections derived from it are the read models.

The pattern is similar in spirit to [Write-Ahead Logging](../Databases/Write-Ahead%20Logging.md): both use an append-only log as the source of truth, with the actual queryable state derived from it.

## Key tradeoffs

- Current state requires a projection or full replay — the raw event store is not directly query-friendly; every new query pattern requires a new projection
- Event schema evolution is hard: old events must remain valid as the schema changes, requiring versioning and upcasting strategies
- Event logs grow without bound; compaction or snapshotting add operational complexity; snapshotting requires serializing the entire state machine

## Related concepts

- [CQRS](CQRS.md) — event sourcing is the natural write model for CQRS; the event log drives the projections that form the read models
- [Write-Ahead Logging](../Databases/Write-Ahead%20Logging.md) — databases use WAL as an append-only record of changes; event sourcing applies the same principle at the application domain level
- [Delivery Semantics](../Messaging/Delivery%20Semantics.md) — event consumers must handle at-least-once delivery and be idempotent; a replayed event must produce the same result as processing it once
