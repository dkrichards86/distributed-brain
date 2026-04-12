# Backpressure

A flow control mechanism that signals upstream producers to slow down when a downstream consumer cannot keep pace.

## Why it matters

In a pipeline where producers emit faster than consumers can process, without backpressure the intermediate buffer grows without bound until memory is exhausted or messages are dropped. Backpressure propagates the constraint upstream, letting the source regulate its own rate to match what the system can absorb. The alternative — silently dropping messages or crashing — is almost always worse.

## How it works

### Reactive streams / pull-based demand

The consumer requests a specific number of items (`request(n)`) and the producer sends at most that many before waiting for the next request. If the consumer is busy, it simply doesn't request more.

The Reactive Streams specification (implemented by RxJava, Project Reactor, Akka Streams) formalizes this contract. The producer is never allowed to send more than the consumer has demanded.

### TCP flow control

TCP implements backpressure at the transport level via the receive window. The receiver advertises how much buffer space it has; the sender limits its in-flight bytes to the window size. When the receiver's buffer fills (consumer too slow), the window shrinks to zero and the sender blocks — backpressure propagated to the application writing to the socket.

### Kafka consumer lag

Kafka consumers pull messages at their own rate. If a consumer falls behind, messages accumulate in the topic (up to the configured retention). The consumer can resume at its own pace — Kafka doesn't push or overwhelm the consumer. Consumer lag is the observable symptom of the consumer being slower than the producer.

### Queue-based backpressure

When a bounded queue fills, producers block (or receive a rejection error). This propagates the signal upstream — the HTTP handler can reject with `503`, the Kafka producer can block the calling thread, or the upstream stage can pause.

### Rate limiting vs. backpressure

Rate limiting caps a producer's output regardless of consumer state (fixed ceiling). Backpressure is adaptive — the producer slows only when the consumer is slow and speeds up when the consumer catches up. Backpressure is preferable when producer and consumer speeds are variable; rate limiting is appropriate when the ceiling is a business or resource constraint independent of consumer state.

## Key tradeoffs

- **Blocking vs. dropping** — when a buffer fills, the system must either block the producer (backpressure) or drop messages; blocking improves correctness but can cause cascading slowdown; dropping is lossy but keeps the system moving
- **Buffer size** — larger buffers absorb bursts but delay the backpressure signal; a 10-million-message buffer means the producer can run unconstrained for a long time before feeling the consumer's slowness
- **End-to-end propagation** — backpressure only helps if it can propagate all the way to the original source; a buffer in the middle of the pipeline that doesn't signal upstream breaks the chain

## Related concepts

- [Pub-Sub Patterns](Pub-Sub%20Patterns.md) — consumer lag and backpressure are the core operational concern of pub-sub systems at scale
- [Rate Limiting](../Engineering/Rate%20Limiting.md) — rate limiting is a producer-side ceiling; backpressure is a consumer-driven signal; they're complementary
- [Load Shedding](../Engineering/Load%20Shedding.md) — when backpressure isn't sufficient to protect the consumer, load shedding deliberately drops low-priority work to protect the system
