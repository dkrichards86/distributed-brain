# Idempotency

An operation is idempotent if applying it multiple times produces the same result as applying it once.

## Why it matters

Distributed systems require retries — networks drop packets, services restart, clients time out. Without idempotency, retries cause duplicate side effects: double charges, duplicate records, or corrupted state. Idempotency is what makes [at-least-once delivery](../Messaging/Delivery%20Semantics.md) safe.

## How it works

The standard approach uses an **idempotency key**: a unique identifier supplied by the caller (a UUID, a client-generated token, a request fingerprint). The server records the key and its result on first execution; subsequent requests with the same key return the cached result without re-executing the operation.

HTTP methods have conventional idempotency semantics: GET, PUT, and DELETE are idempotent by design; POST is not. Non-idempotent POST operations are made safe by adding a server-side idempotency key check.

For message consumers, idempotency is achieved by recording processed message IDs in a durable store (database, Redis) and skipping duplicates — this is the standard pattern for handling [at-least-once delivery](../Messaging/Delivery%20Semantics.md) without exactly-once infrastructure overhead.

## Key tradeoffs

- Requires durable storage to track processed keys and results; adds a read on every incoming request
- Keys must be scoped and eventually expired to bound storage growth — too short a window makes retries unsafe, too long inflates storage cost
- Idempotency doesn't help if the same logical operation is sent with different keys; callers must generate and reuse keys correctly

## Related concepts

- [Retries and Timeouts](../Fault%20Tolerance/Retries%20and%20Timeouts.md) — retries are safe only on idempotent operations; non-idempotent retries require server-side key deduplication
- [Delivery Semantics](../Messaging/Delivery%20Semantics.md) — at-least-once delivery relies on idempotent consumers to be safe; idempotency is the alternative to exactly-once infrastructure
- [Distributed Transactions](../Distributed%20Systems/Distributed%20Transactions.md) — saga compensating transactions must be idempotent; they may be replayed if the orchestrator retries
- [Saga Pattern](../Distributed%20Systems/Saga%20Pattern.md) — each saga step and its compensating transaction must be idempotent to handle retries safely
