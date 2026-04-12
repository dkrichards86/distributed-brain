# Bulkhead

A resource isolation pattern that prevents a failure or slowdown in one call path from exhausting shared resources and degrading unrelated call paths.

## Why it matters

When a service calls multiple downstream dependencies using a shared thread pool or connection pool, one slow dependency can saturate that shared pool. Threads pile up waiting for the slow dependency; threads needed to call healthy dependencies are unavailable. The service degrades entirely even though only one downstream is struggling. Bulkheads partition resources so a failure in one path can't flood the others — named after the watertight compartments on a ship.

## How it works

### Thread pool bulkhead

Each downstream dependency gets its own bounded thread pool. A call to dependency A uses A's pool; a call to dependency B uses B's pool. If dependency A is slow and A's pool fills, new calls to A are rejected immediately — but B's pool is untouched and B's callers are unaffected.

- Strongest isolation: a blocked thread in one pool cannot affect another pool
- Supports async timeouts: the pool's queue can be bounded and a timeout can interrupt a waiting thread
- Overhead: each pool carries its own threads, adding memory and scheduling cost

### Semaphore bulkhead

A semaphore limits the number of concurrent calls to a dependency. When the semaphore count is exhausted, new calls are rejected without blocking a thread.

- Lower overhead than thread pools: no extra threads created
- Weaker isolation: a thread that acquires the semaphore and blocks (e.g., waiting on I/O) holds the semaphore slot and can't be interrupted externally; the pool drains anyway under sustained blocking
- Best for non-blocking or short-lived calls

### Connection pool isolation

Separate HTTP client or database connection pools per downstream dependency. A slow dependency that holds connections can only exhaust its own pool, not the shared one.

### Sizing bulkheads

The pool size should reflect the maximum acceptable concurrency to that dependency at normal load, with some headroom. Too small and you reject requests unnecessarily at normal traffic; too large and the isolation isn't effective. Measure actual concurrency from production traffic, then set a ceiling slightly above the p99.

## Key tradeoffs

- **Isolation vs. efficiency** — dedicated pools are wasteful when dependencies are healthy; threads in A's pool sit idle while B's pool is busy; no work-stealing across pools
- **Thread pools vs. semaphores** — thread pools provide stronger isolation and support external timeout interruption; semaphores are lighter but can't preempt a blocking call
- **Rejection behavior** — when a bulkhead is full, calls are rejected; the caller must handle this gracefully (fallback, queue, error); rejection without a meaningful response just moves the problem
- **Tuning complexity** — each dependency needs its own pool size and queue depth; these must be revisited as traffic patterns change

## Related concepts

- [Circuit Breaker](Circuit%20Breaker.md) — complementary pattern; bulkheads limit resource exhaustion while a dependency is degrading; circuit breakers cut off calls once failure is confirmed; use both together
- [Load Shedding](../Engineering/Load%20Shedding.md) — load shedding protects a service from its own overload; bulkheads protect it from downstream failures; both reject work, but at different points
- [Service Mesh](../Architecture/Service%20Mesh.md) — service meshes can enforce connection limits and concurrency caps at the proxy level, implementing bulkhead semantics without application changes
