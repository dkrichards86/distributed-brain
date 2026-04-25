# CQRS (Command Query Responsibility Segregation)

An architectural pattern that uses separate models — and often separate service paths — for writes (commands) and reads (queries).

## Why it matters

Read and write workloads have different shapes. Writes need strong consistency, validation, and normalized storage. Reads need low latency, flexible projections, and often denormalized data tuned to specific query patterns. A single model optimized for one degrades the other. CQRS lets each side be independently modeled, optimized, and scaled.

## How it works

**Commands** mutate state and return no data (or just an acknowledgment). They are processed by a write model that enforces business rules and updates a normalized source of truth.

**Queries** return data and have no side effects. They are served from one or more read models — denormalized projections optimized for specific access patterns.

The write model updates state and emits an event (or change record). An [event sourcing](Event%20Sourcing.md) log or a change data capture feed propagates updates to the read model(s), which rebuild their projections asynchronously. The read model is eventually consistent with the write model.

CQRS is often paired with [event sourcing](Event%20Sourcing.md): the write side stores events rather than current state, and the read side materializes projections by replaying the event log.

## Key tradeoffs

- Read models are eventually consistent — callers must tolerate stale reads or implement compensating UX (e.g., optimistic updates)
- Two models to maintain: schema changes on the write side must be reflected in every projection; adding a new query pattern requires building a new projection
- Significant complexity overhead; only justified when read/write load profiles genuinely diverge or when multiple distinct query shapes are needed

## Related concepts

- [Event Sourcing](Event%20Sourcing.md) — frequently paired with CQRS; the event log is the write model, and projections are the read models
- [Consistency Models](../Databases/Consistency%20Models.md) — CQRS read models are eventually consistent with the write model; the gap is the same as replication lag
- [Replication](../Databases/Replication.md) — CQRS read models are conceptually similar to read replicas: derived, eventually consistent copies optimized for queries
