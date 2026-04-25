# Delivery Semantics

The guarantee a messaging system makes about how many times a message will be delivered to a consumer.

## Why it matters

In a distributed system, any step — message send, acknowledgment, consumer processing — can fail. The delivery semantic determines which failure mode the system is optimized for and what the consumer must handle. Choosing the wrong semantic either silently drops messages or requires consumers to be idempotent. You can't have exactly-once without overhead; understanding the tradeoffs lets you pick the right guarantee for each use case.

## How it works

### At-most-once

The producer fires and forgets, or the broker delivers without waiting for acknowledgment. A message is delivered zero or one times — never duplicated, but may be lost.

- **When it's right:** metrics, telemetry, log sampling — data where occasional loss is acceptable and duplication is worse (double-counting)
- **Implementation:** producer doesn't retry on failure; consumer doesn't acknowledge before processing; broker doesn't persist messages durably

### At-least-once

The broker delivers a message and waits for acknowledgment. If the ack doesn't arrive (consumer crashes, network drops), the broker redelivers. A message is delivered one or more times — no loss, but possible duplication.

- **When it's right:** most business events — it's safer to process twice than not at all, as long as consumers are idempotent
- **Implementation:** producer retries on failure; broker persists messages until acked; consumer must handle duplicates (idempotency keys, deduplication tables)
- The most common guarantee in practice (Kafka default, SQS standard queues)

### Exactly-once

Each message is delivered and processed exactly one time — no loss, no duplication. The hardest guarantee to implement.

**Two sub-problems:**
1. **Exactly-once delivery** — the broker delivers each message once; typically achieved via idempotent producers and transactional message publishing
2. **Exactly-once processing** — the consumer processes each message once; requires atomically committing the message offset and the side effect together (e.g., in the same database transaction)

- Kafka supports exactly-once semantics within the Kafka ecosystem using the transactional API: idempotent producers prevent duplicate publishes, and consumers commit offsets inside the same transaction as their state update
- Requires all hops to participate; a single non-transactional component breaks the guarantee

### Idempotency as an alternative

Rather than paying the cost of exactly-once infrastructure, most systems implement at-least-once delivery and make consumers idempotent. An idempotent consumer produces the same result whether it processes a message once or ten times — typically by tracking which message IDs have been processed (in a database or cache) and skipping duplicates.

## Key tradeoffs

- **Exactly-once cost** — requires distributed coordination (two-phase commit or transactional APIs); adds latency and reduces throughput
- **At-least-once + idempotency** — simpler infrastructure, but every consumer must implement deduplication; risk of subtle correctness bugs if idempotency isn't handled carefully
- **At-most-once simplicity** — zero overhead but data loss is possible; acceptable only when loss is cheap
- **Scope** — exactly-once is only provable end-to-end within a single system; crossing system boundaries (Kafka → database → third-party API) requires explicit idempotency at each boundary

## Related concepts

- [Pub-Sub Patterns](Pub-Sub%20Patterns.md) — the delivery semantic is a property of the pub-sub broker configuration; consumers are designed around it
- [Distributed Transactions](../Distributed%20Systems/Distributed%20Transactions.md) — exactly-once processing often relies on transactional semantics (atomic offset commit + state update) which is a form of distributed transaction
- [Idempotency](../Engineering/Idempotency.md) — the practical alternative to exactly-once infrastructure; at-least-once delivery is safe when consumers are idempotent
- [Saga Pattern](../Distributed%20Systems/Saga%20Pattern.md) — choreographed sagas rely on at-least-once delivery between services; each step handler must be idempotent
