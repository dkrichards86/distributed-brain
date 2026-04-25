# Saga Pattern

A sequence of local transactions, each publishing an event or message that triggers the next step, with compensating transactions to undo completed steps if a later step fails.

## Why it matters

Distributed transactions across services cannot use a single ACID transaction. [Two-phase commit](Distributed%20Transactions.md) works but requires all participants to be available simultaneously and introduces blocking. Sagas achieve eventual consistency across service boundaries without holding distributed locks or requiring synchronous coordination.

## How it works

Two implementations exist:

**Choreography** — each service listens for events and reacts autonomously. Service A completes its local transaction, publishes an event; Service B subscribes and begins its local transaction; and so on. No central coordinator. Easy to start with but can become hard to reason about as the number of services and event types grows.

**Orchestration** — a saga orchestrator (a dedicated service or workflow engine) explicitly commands each participant in sequence and tracks progress. On failure, the orchestrator issues compensating commands in reverse order to undo completed steps.

**Compensating transactions** must be [idempotent](../Engineering/Idempotency.md) — the orchestrator may retry a compensation if it doesn't receive an acknowledgment. Compensations should be business-meaningful (e.g., `CancelOrder`, `RefundPayment`) rather than low-level rollbacks, since they execute after the fact against a system that may have already acted on the original transaction.

## Key tradeoffs

- Sagas are not atomic in the ACID sense: intermediate states are visible to concurrent operations before the saga completes; other parts of the system may act on partially-committed state
- Compensating transactions can themselves fail, requiring dead-letter queues, manual intervention, or idempotent retries
- Choreography scales well but lacks a global view of saga progress; orchestration centralizes logic and observability but makes the orchestrator a bottleneck and a new point of failure

## Related concepts

- [Distributed Transactions](Distributed%20Transactions.md) — sagas are the primary alternative to 2PC for multi-service atomicity; the two approaches trade ACID isolation for availability and service autonomy
- [Idempotency](../Engineering/Idempotency.md) — each saga step and compensation must be idempotent; retries from the orchestrator or message broker must not cause duplicate effects
- [Delivery Semantics](../Messaging/Delivery%20Semantics.md) — choreographed sagas rely on at-least-once delivery; consumers must be idempotent to handle redelivery
- [Retries and Timeouts](../Fault%20Tolerance/Retries%20and%20Timeouts.md) — the orchestrator retries failed steps with backoff before triggering compensation; retry budgets prevent infinite retry loops
