# Log Levels

A severity hierarchy for log messages that encodes importance and urgency, allowing operators to filter signal from noise.

## Why it matters

Every log line competes for attention. Too much logging overwhelms storage and makes incidents harder to debug. Too little leaves you blind when things break. Log levels let different audiences (developers, operators, incident responders) apply the appropriate filter for their context — and they're the primary lever for controlling logging cost at runtime.

## How it works

Six standard levels, ordered by severity:

| Level | Purpose | Production default? |
|---|---|---|
| `TRACE` | Granular execution detail — function entry/exit, loop state | No — too expensive and verbose |
| `DEBUG` | Diagnostic context — variable values, decision points, control flow | No — enable only when debugging |
| `INFO` | Normal operational events — user actions, business transactions, state changes | Yes |
| `WARNING` | Unexpected but handled — degraded performance, fallbacks activating, conditions that might escalate | Yes |
| `ERROR` | Something failed and requires attention — unhandled exceptions, failed operations | Yes — should be actionable and rare |
| `FATAL` | Critical failure that may terminate the process — corrupt data, exhausted resources | Yes — immediate intervention needed |

### The signal-to-noise problem

The same event can warrant different levels depending on context. A database connection failure in a web scraper (which expects unreachable targets) is `DEBUG`. The same failure in a real-time payment system is `ERROR`. Log levels should reflect business impact, not just technical severity.

**Common mistakes:**
- `INFO` logs that just say "processing request" — too low-value to justify their cost
- `ERROR` logs that don't require action — creates alert fatigue; these are probably `INFO` in disguise
- `WARNING` logs that get routinely ignored — also probably the wrong level
- Leaving `DEBUG` on in production — creates log storms that bury real problems

### Volume as a signal

A single `ERROR` per hour gets attention. A hundred `ERROR`s per hour get ignored. Even legitimate errors lose their impact when buried in volume. Fixing the underlying issue is ideal; rate-limiting is a pragmatic alternative to preserve signal.

### Aggregation window

Short windows for alerting on severity spikes; longer windows for trend analysis. Scanning through `TRACE`/`DEBUG` logs is only practical when targeting a specific investigation. For request-path visibility across services, see [Distributed Tracing](Distributed%20Tracing.md).

## Key tradeoffs

- **Verbosity vs. cost** — `TRACE`/`DEBUG` are invaluable during active debugging but prohibitively expensive at production traffic volumes; dynamic log level adjustment (enable per-request or per-service without restart) is ideal
- **Strictness vs. false alarms** — too-sensitive levels on `ERROR`/`FATAL` create noise and train teams to ignore alerts; too-loose levels mean real problems get missed
- **Context vs. portability** — the right level for an event is contextual, which makes shared library logging hard; libraries should log at `DEBUG` and let applications decide what's worth escalating
