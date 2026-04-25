# Goroutines

Go's lightweight concurrency primitive — a function running concurrently with other goroutines, multiplexed by the Go runtime onto a small pool of OS threads.

## Why it matters

OS threads are expensive (~1–8 MB stack, kernel scheduler overhead). An event loop avoids that cost but constrains you to single-threaded execution with callback/async ceremony. Goroutines sit between: cheap enough (~2–8 KB initial stack, grows dynamically) to spawn by the thousands, yet capable of true parallel execution across CPU cores — no async/await syntax required.

## How it works

The Go runtime implements **M:N scheduling**: M goroutines multiplexed onto N OS threads. `GOMAXPROCS` controls N, defaulting to the number of CPU cores.

Three core abstractions:

| Component | Role |
|---|---|
| **G (goroutine)** | Unit of work; has its own dynamically-sized stack |
| **M (machine)** | OS thread managed by the runtime |
| **P (processor)** | Scheduling context with a local goroutine run queue; an M must hold a P to run goroutines |

Scheduling is **cooperative with preemption**: goroutines yield at channel operations, syscalls, and `runtime.Gosched()`. Since Go 1.14, the runtime can also preempt long-running goroutines via asynchronous signals, preventing a tight loop from starving the scheduler.

### Channels

Goroutines communicate via **channels** — typed, synchronized message-passing primitives that replace shared-memory mutation for most inter-goroutine coordination:

```go
ch := make(chan int)       // unbuffered: send blocks until a receiver is ready
ch := make(chan int, 100)  // buffered: send blocks only when full
```

The runtime parks goroutines blocked on channel ops and resumes them when the operation can proceed — no busy-waiting, no explicit locks needed for the common case.

### Blocking syscalls

When a goroutine makes a blocking syscall, the runtime detaches its M from its P, lets other goroutines run on a new M with that P, then reattaches when the syscall returns. One blocked goroutine doesn't stall the scheduler.

## Key tradeoffs

- **Goroutine leaks** — goroutines that never exit accumulate stack memory and stall GC; always ensure every goroutine has a defined exit path (context cancellation, channel close, etc.)
- **Shared memory still possible** — `sync.Mutex`/`sync.RWMutex` are available and sometimes necessary; data races are still possible and channels don't eliminate them automatically. Use `go test -race`
- **M:N vs. event loop** — goroutines run true parallel CPU work across cores; a single-threaded event loop (e.g. Node.js) cannot without worker threads
- **Stack growth cost** — dynamic stacks eliminate fixed-size thread stack overflow, but stack copying during growth can cause latency spikes under load
- **No goroutine IDs** — intentional design; discourages goroutine-local state and forces explicit parameter passing via function arguments and channels
- **Channels vs. futures** — channels are explicit about communication direction and ownership, but don't compose as easily as future combinators (`Promise.all`, `CompletableFuture.allOf`)

## Related

- [Node.js Event Loop](Node.js%20Event%20Loop.md) — contrast: goroutines run parallel CPU work across threads; Node's event loop is single-threaded and relies on async I/O offloading
- [Futures and Promises](Futures%20and%20Promises.md) — Go channels serve the role that futures/promises play in other languages, with different compositional tradeoffs
- [Request Coalescing](../Performance/Request%20Coalescing.md) — a common pattern implemented with goroutines: one goroutine rebuilds a value while others wait on a channel
