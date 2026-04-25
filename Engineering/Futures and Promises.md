# Futures and Promises

A future is a read-only placeholder for a value that isn't available yet; a promise is the writable handle used to produce it.

## Why it matters

Async systems need a way to represent in-flight work without blocking the caller. Futures and promises formalize this: instead of passing callbacks you pass around a value placeholder that can be chained, awaited, or combined — making concurrent code compositional and avoiding deeply nested callback trees.

## How it works

- **Future** — the consumer side. Holds a reference to a value that may not exist yet. Supports blocking until ready (`.get()`), chaining transforms (`.then()`), or combining multiples (`Promise.all`, `CompletableFuture.allOf`).
- **Promise** — the producer side. Whoever holds the promise resolves or rejects it, which settles the future's value. The caller gets the future; the async worker holds the promise.

The terminology is inconsistent across languages:

| Language | Future concept | Promise concept |
|---|---|---|
| JavaScript | `Promise` (`.then()` side) | `Promise` (settled via `resolve`/`reject` callbacks) |
| Java | `CompletableFuture` | `CompletableFuture` (same object, both roles) |
| Python | `asyncio.Future` | same object |
| Rust | `Future` trait (lazy, poll-driven) | `oneshot::Sender` or similar |
| Go | — | channels (idiomatic replacement for both) |

JavaScript collapses the distinction: a `Promise` is both the read handle and settles via the callbacks passed to its constructor. Rust keeps them strictly separate — a `Future` is lazy and only runs when polled by an executor; the write side lives in a channel sender.

### Eager vs. lazy execution

JavaScript Promises are **eager** — the executor function runs immediately on construction, before any `.then()` is attached. Rust Futures are **lazy** — nothing runs until an async runtime polls the future. This affects when side effects occur and whether spawning a future without awaiting it does any work.

### Composition primitives

- **Sequential** — `.then(f).then(g)`: each transform runs when the previous resolves
- **Parallel** — `Promise.all([f1, f2])`: resolves when all complete; fails fast on first rejection
- **Race** — `Promise.race([f1, f2])`: settles with whichever future resolves or rejects first

`async/await` is syntactic sugar over this same machinery — it desugars to a state machine that chains `.then()` callbacks under the hood.

## Key tradeoffs

- **Eager vs. lazy** — eager futures (JS) start work immediately, which is intuitive but means no way to defer execution; lazy futures (Rust) compose without side effects until explicitly driven
- **Error propagation** — unhandled rejections silently swallow errors in many runtimes; always attach a `.catch()` or wrap `await` in `try/catch`
- **Cancellation** — first-class cancellation is absent from most implementations; `AbortController` (JS) and `context.Context` (Go) are bolt-on solutions
- **Debugging** — async stack traces are truncated at suspension points; the logical call stack doesn't match the OS stack, making errors hard to trace
- **Channels as an alternative** — Go replaces futures entirely with channels, which make the communication explicit and avoid the producer/consumer role confusion

## Related

- [Node.js Event Loop](Node.js%20Event%20Loop.md) — Promises are microtasks in Node; understanding which queue they land in affects execution order
- [Goroutines](Goroutines.md) — Go's concurrency model uses channels instead of futures; a different tradeoff between explicitness and composability
