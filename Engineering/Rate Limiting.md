# Rate Limiting

A technique that controls how many requests a client can make to a service within a time window, enforced at the service boundary.

## Why it matters

Without rate limiting, any single client — whether misbehaving, misconfigured, or malicious — can consume unbounded server resources. This causes the "noisy neighbor" problem: one client's traffic degrades service for all others. Rate limiting creates isolation: each client gets a fair share, and exceeding it is their problem, not everyone else's.

It also provides a predictable load ceiling. Downstream dependencies (databases, external APIs) are sized for a certain request rate. Rate limiting ensures that ceiling is never exceeded regardless of what clients do.

## How it works

**Common algorithms:**

**Token bucket** — a bucket holds up to N tokens; tokens replenish at a fixed rate. Each request consumes one token. If the bucket is empty, the request is rejected. Allows bursting up to the bucket capacity, then enforces the average rate.

```
tokens = min(capacity, tokens + rate * elapsed_time)
if tokens >= 1: tokens -= 1; allow
else: reject
```

**Leaky bucket** — requests enter a fixed-size queue and are processed at a constant rate. Excess requests beyond the queue size are dropped. Smooths traffic to a constant output rate; no bursting allowed.

**Fixed window** — count requests in the current time window (e.g., this minute). Reset the counter at the window boundary. Simple, but vulnerable to burst at window boundaries: a client can send N requests at 11:59 and N requests at 12:00, sending 2N in a two-second span.

**Sliding window** — track request timestamps; count only those within the last N seconds. Eliminates the boundary burst problem; more memory-intensive.

**Sliding window counter** — a hybrid: blend the count from the previous window with the current window based on overlap. Approximates sliding window with O(1) memory per key.

**Scope:**

- **Per-client / per-API-key** — isolates tenants; the most common form
- **Per-IP** — useful when clients aren't authenticated; easily bypassed with IP rotation
- **Global** — total request rate cap regardless of source; protects against aggregate overload
- **Per-endpoint** — different limits for expensive vs. cheap operations

**Storage:** limits are typically enforced using Redis (`INCR` + `EXPIRE`, or Lua scripts for atomic check-and-increment). For low-precision limits, in-process counters (per instance) are cheaper but don't aggregate across replicas.

**Returning the right response:** rejected requests should return `429 Too Many Requests` with `Retry-After` and `X-RateLimit-*` headers so clients know when they can retry and how much quota remains.

## Key tradeoffs

- **Token bucket vs. leaky bucket** — token bucket allows bursting (good for bursty but well-behaved clients); leaky bucket enforces strict smoothing (good for protecting downstream systems that can't absorb bursts)
- **Distributed vs. local enforcement** — Redis-backed rate limiting is accurate across replicas but adds latency per request; local in-process limiting is fast but each instance enforces independently, allowing N× the intended rate across N replicas
- **Proactive vs. reactive** — rate limiting is proactive (per-client ceiling before a problem develops); [Load Shedding](Load%20Shedding.md) is reactive (system-wide when already under stress); both are needed
- **Fairness vs. priority** — uniform per-client limits are fair but don't distinguish high-value traffic from low-value traffic; tiered limits (paid vs. free) add complexity but better reflect business value
