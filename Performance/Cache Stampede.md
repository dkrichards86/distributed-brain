# Cache Stampede

A [Thundering Herd](Thundering%20Herd.md) event specific to caches: a popular entry expires and many concurrent requests all miss simultaneously, each independently triggering an expensive backend rebuild.

## Why it matters

A cache entry expiring is supposed to be a non-event — one miss, one backend call, cache repopulated. Under high traffic it isn't. If 500 requests per second are hitting a key and it expires, hundreds of requests see the miss in the time it takes to rebuild the value. Each one independently queries the database. The database absorbs a spike it was never sized for, latency degrades for all users, and under extreme load the database can fall over entirely — taking the cache with it.

## How it works

The stampede window is the rebuild duration. A key that takes 200ms to rebuild at 500 req/s exposes ~100 concurrent miss requests. That's 100 redundant database queries for one logical cache miss.

**Prevention strategies:**

**[Request Coalescing](Request%20Coalescing.md) (singleflight)** — within a single process, collapse all concurrent misses for the same key into one backend call. All waiters share the result. Eliminates redundant work entirely, but only within one process. Across 10 instances, each can still independently trigger the same query.

**Probabilistic early expiration (XFetch)** — instead of a hard TTL, each cache read has a probability of triggering a background refresh that increases as the entry approaches expiry. The entry is refreshed before it expires, so a miss never occurs. No locks or coordination needed.

```
score = current_time - (ttl_remaining * log(random()))
if score > expiry_time: refresh in background
```

**Stale-while-revalidate** — serve the stale value immediately, kick off a background refresh. Latency never spikes; the tradeoff is that clients briefly see stale data. Built into HTTP `Cache-Control: stale-while-revalidate=N`.

**[Jitter](Jitter.md) on TTLs** — if many keys are set simultaneously with the same TTL (e.g., after a cache flush or bulk write), they all expire simultaneously. Adding `TTL = base + rand(0, spread)` staggers expirations and smooths the rebuild load over time.

**Mutex / distributed lock** — only one process may rebuild; others wait or serve stale. Simple but adds lock contention and a single point of failure for rebuild work.

## Key tradeoffs

- **Request coalescing** solves redundant work but is per-process; distributed coalescing needs coordination
- **Probabilistic early expiration** prevents the miss entirely but requires the cache client to implement the XFetch algorithm and accept background load during the approach to TTL
- **Stale-while-revalidate** gives zero-latency reads at the cost of briefly stale data — acceptable for content, problematic for financial or inventory data
- **Jitter** is cheap and broadly applicable but requires discipline at every cache write site
