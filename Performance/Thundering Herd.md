# Thundering Herd

A failure pattern where many waiting processes or threads are simultaneously unblocked and rush to acquire the same resource, overwhelming it.

## Why it matters

A system can be sized correctly for steady-state load and still collapse under thundering herd conditions — because the problem isn't total capacity, it's the synchronized burst. The resource being targeted (a database, a lock, a connection pool) can't absorb demand that arrives all at once even if it could handle the same requests spread over time.

## How it works

The pattern requires three ingredients:

1. **Many waiters** — processes/threads/requests blocked on a condition
2. **A single trigger** — the condition satisfies and all waiters are notified simultaneously
3. **Contention** — all waiters now compete for a resource that can only serve a fraction of them at once

**Common instances:**

| Scenario | The condition | The resource stampeded |
|---|---|---|
| [Cache Stampede](Cache%20Stampede.md) | Cache entry expires | Database / backend service |
| Connection pool exhaustion | One connection returned | All threads wake and race for it |
| Retry storms | Backoff timer fires | The service being retried |
| Linux `accept()` (historic) | New connection arrives | All processes blocked on accept wake |
| Cold startup | Service boots | Downstream dependencies hit simultaneously |

**Why retries are especially dangerous:** if clients retry on failure using a fixed backoff interval, they all back off for the same duration and then all retry at the same time. This turns a brief overload spike into a sustained oscillation — the system gets overwhelmed, all requests fail, all clients back off together, then all hammer again.

## Key tradeoffs

- **[Jitter](Jitter.md)** — randomizing TTLs, backoff intervals, or sleep durations breaks synchronization cheaply; the tradeoff is slightly less predictable behavior
- **[Request Coalescing](Request%20Coalescing.md)** — merges concurrent duplicate requests into one; eliminates the problem for identical requests but only works within a single process
- **[Load Shedding](../Engineering/Load%20Shedding.md) and [Rate Limiting](../Engineering/Rate%20Limiting.md)** — absorb the burst by rejecting excess demand; treats the symptom rather than preventing the synchronization
- **Staggered wakeup** — some runtimes (Linux kernel, modern load balancers) distribute notifications instead of broadcasting; requires runtime support
