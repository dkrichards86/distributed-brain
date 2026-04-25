# Node.js Event Loop

Node.js's execution model that allows a single-threaded runtime to handle asynchronous I/O without blocking.

## Why it matters

Node runs JavaScript on a single thread, but handles thousands of concurrent connections efficiently by offloading I/O to the OS and processing callbacks when operations complete. Understanding the loop matters when refactoring async code — moving from callback-based patterns to Promises/async-await changes which queue operations land in, which changes execution order and can starve I/O handlers.

## How it works

The event loop has six phases, each with its own callback queue:

| Phase | What runs |
|---|---|
| **Timers** | `setTimeout()` and `setInterval()` callbacks whose delay has elapsed |
| **Pending callbacks** | I/O callbacks deferred from the previous iteration |
| **Idle, prepare** | Internal Node.js housekeeping (not application code) |
| **Poll** | Fetch and execute new I/O events; blocks here if no timers are scheduled |
| **Check** | `setImmediate()` callbacks |
| **Close callbacks** | Socket/handle close event callbacks |

These are **macrotasks** — events from I/O or APIs, processed one phase at a time.

### Microtasks

Microtasks run between *every* phase — after each phase completes, the entire microtask queue is drained before the next phase begins.

**Microtask priority order (highest to lowest):**
1. `process.nextTick()` — runs before any other async operation
2. Promise callbacks (`.then()`, `async/await` continuations)
3. `queueMicrotask()`

**Key implication:** Promises are microtasks. Callbacks scheduled by the legacy `async` library are macrotasks. Converting `async.parallel`/`async.waterfall` to `Promise.all`/`await` moves those completions from the macrotask queue to the microtask queue — they will now resolve before any pending I/O or timers.

### The refactor risk

Excessive microtasks can starve the Poll phase. If a chain of resolved Promises keeps queuing new microtasks, the event loop never advances to the I/O phase, and timer callbacks pile up. At high request volumes, subtle differences in when control returns to the event loop compound quickly.

**Monitoring signals to watch:**
- Event loop lag (time between scheduling and execution)
- Time spent per phase
- Microtask queue depth

## Key tradeoffs

- **Microtasks vs. macrotasks** — microtasks complete before I/O, which can improve responsiveness for Promise-heavy code but can starve I/O handlers under heavy microtask load
- **`process.nextTick()` priority** — fires before Promises, so recursive `nextTick` chains can indefinitely block all other async work
- **`setImmediate()` vs. `setTimeout(0)`** — `setImmediate` is guaranteed to run in the Check phase after I/O; `setTimeout(0)` runs in Timers which may fire before or after I/O depending on system load
- **Single-threaded CPU work** — any synchronous CPU-intensive operation blocks the entire loop; Node is not suited for CPU-bound work without worker threads

## Related

- [Futures and Promises](Futures%20and%20Promises.md) — Promises are microtasks in Node; which queue they land in determines execution order relative to I/O
- [Goroutines](Goroutines.md) — contrast: goroutines multiplex across OS threads for true parallelism; the event loop achieves concurrency on a single thread via async I/O

