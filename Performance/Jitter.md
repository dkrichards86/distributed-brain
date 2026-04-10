# Jitter

The deliberate addition of randomness to timing values in distributed systems to prevent synchronized behavior that causes load spikes.

## Why it matters

Many distributed systems problems arise not from total load but from synchronized load — requests arriving all at once because they were started, expired, or scheduled at the same time. [Thundering Herd](Thundering%20Herd.md) events, retry storms, and cache expiration waves are all synchronization problems. Jitter is the simplest fix: if timing is random, behavior cannot synchronize.

## How it works

**Cache TTL jitter** — if many cache entries are populated at the same time (cache flush, bulk load, deployment), they all expire at the same time, triggering a [Cache Stampede](Cache%20Stampede.md). Adding randomness staggers expirations:

```
ttl = base_ttl + random(0, spread)
# e.g., 60s + random(0, 15s) → expirations spread over 75s window
```

**Retry backoff jitter** — fixed or purely exponential backoff causes retry storms: all clients fail, all back off for the same interval, all retry simultaneously, all fail again. Jitter breaks this cycle:

```
# Pure exponential (bad under load):
sleep = base * 2^attempt

# Full jitter (breaks synchronization):
sleep = random(0, base * 2^attempt)

# Equal jitter (balances spread with minimum floor):
sleep = (base * 2^attempt / 2) + random(0, base * 2^attempt / 2)
```

AWS wrote the canonical analysis on this — full jitter significantly outperforms fixed and decorrelated jitter for reducing server load during retry storms.

**Scheduled task jitter** — cron jobs or periodic tasks that run on exact intervals across many workers synchronize by definition. Staggering start times (or adding a random sleep at startup) spreads the load:

```
sleep(random(0, period))
# then start the periodic loop
```

**Leader election / heartbeat jitter** — in consensus systems, election timeouts include randomness by design (Raft uses `150ms–300ms`). Without jitter, all nodes time out at the same moment and split votes indefinitely.

## Key tradeoffs

- **Simplicity** — a single `+ rand(0, N)` is often the entire implementation; no infrastructure required
- **Reduced predictability** — timing guarantees become probabilistic rather than exact; harder to reason about worst-case latency or staggered task completion
- **Spread vs. floor** — full jitter minimizes server load but allows very short retries; equal jitter guarantees a minimum backoff floor; choose based on whether protecting the server or protecting the client matters more
- **Doesn't eliminate root causes** — jitter treats synchronization; it doesn't fix an overloaded backend, a cache that's too small, or a retry rate that's too high
