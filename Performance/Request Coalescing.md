# Request Coalescing

A technique that consolidates concurrent duplicate requests for the same resource into a single upstream operation, sharing the result with all waiters.

## Why it matters

When a popular cache entry expires under high traffic, dozens or hundreds of concurrent requests can simultaneously encounter the miss and each independently trigger an expensive backend operation. This is a [Cache Stampede](Cache%20Stampede.md) — a form of [Thundering Herd](Thundering%20Herd.md) — redundant work that spikes database connections, degrades latency, and requires you to provision for worst-case stampede loads rather than actual traffic. Request coalescing eliminates the redundant work at the source.

## How it works

When a request needs to rebuild a cache entry:
1. Check if another goroutine/thread is already rebuilding that key
2. If not — become the "owner," start the rebuild
3. If yes — wait for the owner's result instead of starting duplicate work
4. When the rebuild completes, all waiters receive the result simultaneously

In Go, `singleflight.Group.Do(key, fn)` implements this:

```go
func getExpensiveData(key string) (string, error) {
    result, err, _ := group.Do(key, func() (interface{}, error) {
        return fetchFromDatabase(key)
    })
    return result.(string), err
}
```

Ten concurrent calls with the same key result in one database query. The other nine receive the same result when it completes.

### Why this is better than cache locking

Traditional cache locking acquires a distributed lock before rebuilding. Problems:
- Lock contention becomes a bottleneck
- If the rebuilding request fails, all waiters are stuck until the lock times out
- Requires distributed coordination

Coalescing is local (per process), coordination-free, and degrades gracefully — each coalescing group is independent, so a failure in one key doesn't block other keys.

### When it works best

- High concurrency on the same keys (social media feeds, product catalogs, popular content)
- Expensive operations: DB queries, external API calls, complex computations
- Idempotent operations — multiple requests for the same data should return the same result

### When it doesn't help much

- Requests spread across mostly-unique keys (coalescing has nothing to merge)
- Low-concurrency workloads where stampede never actually occurs

## Key tradeoffs

- **Blast radius of failure** — if the single executing request fails, all coalesced waiters fail together; retries must be handled carefully
- **Latency tail** — all coalesced requests experience the full rebuild latency, not just the one that triggered it; there's no way to serve a fast cached response while rebuilding
- **Memory pressure** — waiting requests accumulate in memory; under extreme load, many keys coalescing simultaneously increases heap usage
- **Scope** — `singleflight` is per-process; if you have 10 instances, each can independently trigger the same upstream query; distributed coalescing requires coordination (e.g., Redis locks)
