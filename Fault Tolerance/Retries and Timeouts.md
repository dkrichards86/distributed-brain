# Retries and Timeouts

Two complementary resilience techniques: timeouts bound how long a caller waits for a response; retries re-attempt a failed request in the hope that a transient fault has cleared.

## Why it matters

In a distributed system, any call can fail or stall — a network blip, a momentarily overloaded backend, a GC pause. Without timeouts, a caller waits indefinitely, holding resources (threads, connections, memory) until either the response arrives or the process is killed. Without retries, transient faults that would resolve in milliseconds cause visible errors. Together, they make a service resilient to the transient failures that are unavoidable at scale.

## How it works

### Timeouts

A timeout is a deadline: if a response hasn't arrived within N milliseconds, abort the call and return an error.

**Types:**
- **Connection timeout** — how long to wait to establish the connection (TCP handshake). Short; a connection that takes >1s usually indicates a routing problem.
- **Request timeout** — how long to wait for the full response after the connection is established. The primary knob.
- **Deadline propagation** — in a chain of services (A → B → C), A's deadline should be propagated to B and C. If A times out in 500ms, there's no point in B waiting 2 seconds for C. gRPC and some HTTP frameworks propagate deadlines automatically via headers.

Setting timeouts:
- Too short: healthy requests are aborted; artificially elevated error rate
- Too long: failed backends hold threads/connections for their full duration, risking thread pool exhaustion (the condition [bulkheads](Bulkhead.md) contain)
- Baseline: set to the p99 latency of the call under normal load, with some headroom

### Retries

A retry re-sends a failed request to the same or a different backend instance. Useful for:
- Connection failures (backend was restarting, TCP RST)
- HTTP 503 / 429 (transient overload)
- Idempotent operations where re-execution is safe

**What not to retry:**
- Non-idempotent operations (POST, payment processing) — retrying may cause duplicate side effects
- HTTP 400/401/403/404 — client errors; retrying won't change the outcome
- Responses that arrived but were slow — if the request completed on the server, retrying may apply it twice

### Retry limits and backoff

Unlimited retries are worse than no retries — they amplify load on an already-struggling backend.

**Limits:** cap total retry attempts (2–3 is typical) and total retry budget (e.g., no more than 10% of requests in a time window are retries).

**Exponential backoff:** wait `base * 2^attempt` between retries (e.g., 100ms, 200ms, 400ms). Gives the downstream time to recover between attempts.

**Jitter:** add randomness to backoff (`wait * random(0.5, 1.5)`). Prevents a fleet of callers that all failed at the same moment from retrying in lockstep and creating a [thundering herd](../Performance/Thundering%20Herd.md). See [Jitter](../Performance/Jitter.md).

### Retry storms

If a backend becomes slow and every caller retries, the total request rate to the backend multiplies by the retry count. The backend, already struggling, receives more load and degrades further. This is a **retry storm**.

Mitigations:
- Retry budgets (cap the fraction of traffic that can be retries)
- [Circuit breakers](Circuit%20Breaker.md) — once the failure rate crosses a threshold, stop sending requests entirely rather than retrying
- Retry-After headers — the server signals how long to back off

## Key tradeoffs

- **Retries amplify load** — retries are only safe when the backend can absorb the extra traffic; during an outage, they can make recovery harder; circuit breakers are the circuit-breaker for retry storms
- **Idempotency requirement** — retries on non-idempotent operations require idempotency keys or deduplication at the server; see [Delivery Semantics](../Messaging/Delivery%20Semantics.md)
- **Timeout length vs. tail latency** — a short timeout cuts off slow requests but hides the p99 problem from visibility; the underlying slowness should be fixed, not masked by short timeouts
- **Deadline propagation** — without deadline propagation, downstream services continue work after the upstream has already given up, wasting resources

## Related concepts

- [Circuit Breaker](Circuit%20Breaker.md) — circuit breakers sit above retries; when retries repeatedly fail, the circuit opens and stops the storm before it amplifies load
- [Bulkhead](Bulkhead.md) — bounded thread pools prevent slow calls (from timeouts not firing fast enough) from exhausting shared resources
- [Jitter](../Performance/Jitter.md) — randomizing retry backoff intervals prevents synchronized retry storms from a fleet of callers
- [Thundering Herd](../Performance/Thundering%20Herd.md) — synchronized retries are a form of thundering herd; the same problem, triggered by failure rather than cache expiry
- [Delivery Semantics](../Messaging/Delivery%20Semantics.md) — retries in messaging systems are the mechanism behind at-least-once delivery; idempotency is the consumer-side contract that makes retries safe
- [Service Mesh](../Architecture/Service%20Mesh.md) — service meshes apply retry and timeout policies at the proxy level, consistently across all services, without application code changes
- [Idempotency](../Engineering/Idempotency.md) — the server-side property that makes retries safe; non-idempotent operations require idempotency keys to prevent duplicate side effects
- [Saga Pattern](../Distributed%20Systems/Saga%20Pattern.md) — saga orchestrators retry failed steps before triggering compensation; retry budgets prevent infinite retry loops across a multi-service workflow
