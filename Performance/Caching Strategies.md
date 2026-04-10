# Caching Strategies

Patterns for when and how to populate a cache and keep it consistent with the backing data store.

## Why it matters

Caching is about optimizing reads — but the mechanics of how you populate, update, and invalidate the cache determine correctness, consistency, and how much complexity leaks into your application code.

## How it works

### Core read strategies

**Cache-aside (lazy loading)**

The application manages the cache directly.

1. Check cache
2. On miss: fetch from DB, write to cache, return result
3. On hit: return cached value

- Application has full control over what gets cached and when
- Cache miss adds one extra round trip
- Race condition: between the DB read and the cache write, concurrent requests may also miss and duplicate the work
- Best for: predictable read patterns, infrequently changing data, cases where you need business-specific caching logic

**Read-through**

The cache layer sits between the application and the store. On a miss, the *cache* fetches from the backing store and populates itself.

- Application always reads from the cache; no miss-handling code
- Less control over what gets cached or when
- Best for: straightforward access patterns where you want caching concerns out of application code

---

### Optimization techniques (layer on top of either strategy)

**Cache warming**

Pre-load data before it's requested — during deployment, at startup, or during low-traffic windows.

- Eliminates cold-start penalty for the first users after a cache flush
- Only effective when access patterns are predictable enough to know what to warm
- Warming the wrong data wastes capacity and may evict useful entries

**Refresh-ahead**

The cache proactively refreshes frequently-accessed entries before they expire, in the background.

- Hot data never actually expires and causes a miss
- Extra load on the backing store for background refreshes
- Best for: stable datasets where popular items stay popular over time

---

### Write strategies

| Strategy | Behavior | Trade-off |
|---|---|---|
| **Write-through** | Write to cache and DB together | Consistent; write latency is higher |
| **Write-around** | Skip cache, write directly to DB | Prevents cache pollution from rarely-read data; next read is a miss |
| **Write-back** | Write to cache first, DB later | Fastest writes; risk of data loss if cache fails before flush |

Most applications use write-through or write-around depending on whether consistency or write performance is the priority.

## Key tradeoffs

- **Control vs. simplicity** — cache-aside gives fine-grained control at the cost of cache logic spread across the application; read-through is simpler but delegates decisions to the cache layer
- **Consistency** — write-through is consistent; write-back is fast but risks loss; invalidation on write is simple but creates a miss on the next read
- **Race conditions** — cache-aside has a window between miss and populate where duplicate work happens ([Cache Stampede](Cache%20Stampede.md)); [Request Coalescing](Request%20Coalescing.md) (singleflight) solves this within a process; [Jitter](Jitter.md) on TTLs prevents synchronized expirations
- **Warming vs. eviction** — pre-warming a large cache can evict entries that users were actually hitting; warming requires knowing your access patterns

