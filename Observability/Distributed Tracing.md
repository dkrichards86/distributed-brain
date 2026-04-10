# Distributed Tracing

A technique for following a single request's path through a distributed system, recording where time is spent and where failures occur across service boundaries.

## Why it matters

[[Metrics and Percentiles|Metrics]] tell you *that* something is slow. [[Log Levels|Logs]] tell you what happened at individual moments. Tracing tells you *where* time was spent and how operations relate to each other. In a distributed system, a single user-facing request may touch a dozen services — tracing is the only tool that shows the full picture.

## How it works

A **trace** represents the complete lifecycle of one request, from entry point to response.

A **span** represents a single unit of work within that trace — a function call, database query, HTTP call to another service, etc. Spans have:
- Start time and end time (duration)
- Service name and operation name
- Status (success or error)
- Custom attributes (user ID, feature flags, entity IDs)
- Parent span reference

Spans are hierarchical: child spans nest under their parent, forming a tree. The tree maps to your system's call graph.

**Cross-service propagation:** Tracing libraries inject a trace context header into outgoing HTTP requests, which downstream services extract and use to parent their spans correctly. This is how a trace stays coherent across service boundaries without central coordination.

### Reading a trace

Start with the overall timeline (usually shown as a waterfall chart):
1. How long did the entire request take?
2. Which span consumed the most time?
3. Are there serial operations that could run in parallel?
4. Where did errors occur, and what work was wasted as a result?

A span that takes 90% of the parent span's duration is your bottleneck. Drill into it; check if its children explain the time.

### Sampling

Tracing every request at high traffic is expensive in CPU and storage. Most systems use sampling:

- **Head sampling** — decide at trace start whether to record (fast, but you lose visibility into rare errors)
- **Tail sampling** — record everything, decide what to keep after the fact (captures errors and slow traces; more expensive)
- **Adaptive sampling** — increase sample rate automatically when errors spike or latency degrades

### When tracing is most valuable

- Performance problems in distributed systems ("why is this endpoint sometimes slow?")
- Cascading failures — traces show the dependency chain and distinguish root cause from symptoms
- Complex async workflows where a request spawns background jobs across services
- Debugging issues that only affect specific users or entity types (filter traces by attribute)
- Diagnosing which services are burning your [[SLOs and Error Budgets|error budget]]

### Compared to logs

| | Logs | Traces |
|---|---|---|
| Unit | Point-in-time event | Span of work with duration |
| Structure | Independent lines | Hierarchical tree |
| Best for | What happened, what the system was thinking | Where time was spent, how operations relate |
| Volume | One line per event | One span per unit of work |

## Key tradeoffs

- **Sampling rate vs. visibility** — lower sampling reduces cost but may miss intermittent issues and rare error paths
- **Automatic vs. manual instrumentation** — frameworks auto-instrument HTTP and DB calls; the most valuable spans (business logic) require manual instrumentation
- **Projection scope** — too many custom attributes bloat span size and storage costs; too few make traces unsearchable
- **Overhead** — tracing adds CPU and memory overhead to every instrumented operation; typically small per-request but measurable at scale

