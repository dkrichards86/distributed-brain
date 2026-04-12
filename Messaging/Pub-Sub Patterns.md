# Pub-Sub Patterns

A messaging model where producers publish messages to named topics and consumers subscribe to receive them, decoupling the sender from the receiver.

## Why it matters

In a direct call model (RPC, HTTP), the sender must know the receiver's address and the receiver must be available. Pub-sub removes both constraints: producers and consumers are decoupled in time, identity, and count. A single publish event can fan out to many consumers, and consumers can be added or removed without changing the producer.

## How it works

### Core model

- **Producer** publishes a message to a **topic** (Kafka) or **exchange** (RabbitMQ) without knowing who will receive it
- **Broker** stores and routes messages
- **Consumer** subscribes to a topic and receives messages; may acknowledge receipt to advance the broker's delivery pointer

### Topic-based vs. content-based routing

- **Topic-based** — consumers subscribe to named topics; all messages on a topic are delivered to all subscribers. Simple and high throughput.
- **Content-based** — consumers declare a filter expression; the broker evaluates message attributes against filters to decide delivery. Flexible but expensive to evaluate at scale.

### Consumer groups (Kafka-style)

A consumer group is a set of consumers that collectively process a topic's partitions. Each partition is assigned to exactly one consumer in the group at a time, providing parallel consumption while guaranteeing each message is processed once per group. Different consumer groups each receive a full copy of all messages — this is the fan-out mechanism.

### Queue vs. pub-sub

- **Queue (point-to-point)** — each message is delivered to exactly one consumer. Used for work distribution. RabbitMQ queues and Kafka consumer groups behave this way within a group.
- **Pub-sub (broadcast)** — each message is delivered to all subscribers. Used for event notification, cache invalidation, read model updates.

Most brokers (Kafka, RabbitMQ, Pulsar) support both models depending on subscription configuration.

### Message ordering

Brokers make different ordering guarantees:
- Kafka guarantees order within a partition; messages on different partitions can interleave
- RabbitMQ guarantees FIFO within a single queue
- SNS/SQS makes no ordering guarantee by default (SQS FIFO queues are the exception)

## Key tradeoffs

- **Decoupling vs. observability** — async messaging makes it harder to trace a request end-to-end; [distributed tracing](../Observability/Distributed%20Tracing.md) and correlation IDs are required to maintain visibility
- **Fan-out cost** — broadcasting to many consumers multiplies storage and network cost by subscriber count; pull-based systems (Kafka) handle this better than push-based systems
- **Delivery semantics** — the broker's delivery guarantee ([at-least-once, at-most-once, exactly-once](Delivery%20Semantics.md)) determines what the consumer must handle
- **Consumer lag** — if consumers can't keep up with producers, messages accumulate; [backpressure](Backpressure.md) mechanisms prevent unbounded queue growth

## Related concepts

- [Delivery Semantics](Delivery%20Semantics.md) — the guarantee the broker makes about how many times a message is delivered; consumers must design for the weakest guarantee the broker provides
- [Backpressure](Backpressure.md) — what happens when consumers are slower than producers; critical for preventing broker saturation
