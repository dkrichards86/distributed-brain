# Circuit Breaker

A stability pattern that stops a caller from repeatedly attempting calls to a failing downstream service, giving the downstream time to recover while preventing the caller's thread pool from filling with stuck requests.

## Why it matters

When a downstream service is slow or unavailable, calls to it don't fail fast — they hang until a timeout fires. If many callers are making these calls concurrently, their thread pools fill with waiting threads. The caller becomes unable to serve its own requests, and the failure cascades upstream. A circuit breaker short-circuits this by detecting the failure and rejecting calls immediately, without waiting for a timeout.

## How it works

The circuit models the call to a downstream service as an electrical circuit with three states:

**Closed (normal)** — requests flow through. The breaker tracks failures (errors, slow responses above a threshold) in a rolling window. If the failure rate or count exceeds a configured threshold, the circuit **opens**.

**Open (failing fast)** — requests are rejected immediately without touching the downstream service. The caller receives an error or a fallback response without paying timeout latency. This gives the downstream service space to recover and stops the cascade.

**Half-open (probing)** — after a configured cooldown, the circuit allows a small number of test requests through. If they succeed, the circuit closes and normal traffic resumes. If they fail, it opens again and the cooldown resets.

Key configuration parameters:
- **Failure threshold** — e.g., 50% error rate over a 10-second rolling window
- **Minimum request volume** — don't open on 1 failure out of 1 request; require meaningful sample size
- **Cooldown duration** — how long to stay open before probing
- **Failure definition** — errors only, or also slow responses above a latency threshold

Implemented by Hystrix (Netflix, now in maintenance), Resilience4j, Polly, and as a first-class feature of most [service meshes](../Architecture/Service%20Mesh.md).

## Key tradeoffs

- **Fallback quality** — failing fast only helps if the caller has a meaningful fallback; returning an error to the end user just moves the failure one hop upstream rather than absorbing it
- **Threshold sensitivity** — a threshold too low trips on transient blips and causes unnecessary outages; too high misses real failures and lets thread pools drain; tuning requires real traffic data
- **Half-open race condition** — multiple instances of a service may all probe simultaneously during half-open; coordinate with a shared state store (Redis) or accept occasional thundering herd on recovery
- **Observability** — a circuit breaker that opens silently is useless; every state transition (closed → open, open → half-open, half-open → closed) must emit a metric and alert

## Related concepts

- [Bulkhead](Bulkhead.md) — complementary pattern; bulkheads bound resource exhaustion, circuit breakers stop calls once failure is detected; use both together
- [Failure Detection](Failure%20Detection.md) — circuit breakers detect failure at the service-call level; heartbeats and phi accrual detect it at the node level
- [Chaos Engineering](Chaos%20Engineering.md) — chaos experiments deliberately trigger conditions that should open the breaker to verify it works correctly under real load
- [Service Mesh](../Architecture/Service%20Mesh.md) — service meshes implement circuit breaking in the sidecar proxy, removing the need to implement it in application code
