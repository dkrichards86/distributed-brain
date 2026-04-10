# Load Shedding

The deliberate rejection of requests when a system is near or over capacity, trading availability for a subset of users to preserve stability for the rest.

## Why it matters

An overloaded service doesn't gracefully degrade — it often collapses entirely. Queues fill, latency climbs, in-flight work takes longer, which causes more work to queue, which causes more latency. Without a relief valve, a traffic spike turns into a cascading failure. Load shedding is the relief valve: by dropping some requests early, the system protects its ability to serve the rest.

The alternative — trying to process everything — typically produces worse outcomes: every request experiences degraded latency, queued work may time out before it's processed (wasted work), and downstream dependencies can be overwhelmed, spreading the failure.

## How it works

Load shedding decisions require two things: a signal that load is too high, and a policy for which requests to drop.

**Signals:**

- Queue depth exceeding a threshold
- CPU or memory above a utilization ceiling
- Latency percentiles (p95, p99) above SLO
- Explicit capacity counter (tokens available, concurrency limit reached)

**Drop policies:**

| Policy | Mechanism | Best for |
|---|---|---|
| **Random** | Drop each request with probability p | Simple; no knowledge of request value needed |
| **Priority-based** | Assign tiers; drop lower tiers first | When you can distinguish critical vs. non-critical requests |
| **LIFO queue drain** | Drop the most recently queued requests | Newest arrivals have the most value (stale requests likely to time out) |
| **Tail drop** | Drop all requests once a queue limit is reached | Simplest; prevents unbounded queue growth |

**Returning the right error:** a shed request should return `503 Service Unavailable` with a `Retry-After` header. This signals to clients that the system is temporarily saturated — not broken — and tells well-behaved clients to back off. Without this signal, clients retry immediately, worsening the overload.

**Relation to [Rate Limiting](Rate%20Limiting.md):** rate limiting controls *how fast* a client can send requests (proactive, per-client). Load shedding controls *whether* the server accepts a request given its current state (reactive, system-wide). They're complementary — rate limiting prevents the overload from forming; load shedding handles it when it arrives anyway.

## Key tradeoffs

- **Partial availability vs. total failure** — shedding 20% of requests lets 80% succeed; without shedding, 100% may degrade to timeout
- **Which requests to drop** — random shedding is fair but may drop high-value requests; priority shedding requires clients to signal request importance, which is gameable
- **Client behavior** — load shedding only helps if clients respect the 503 and back off; aggressive retry-on-503 turns shedding into [Thundering Herd](../Performance/Thundering%20Herd.md) again; [Jitter](../Performance/Jitter.md)ed backoff is the expected client behavior
- **Detecting false positives** — misconfigured thresholds cause unnecessary shedding during normal load; thresholds need tuning against real traffic profiles
