# SLOs and Error Budgets

A principled reliability framework that defines measurable targets (SLOs), tracks allowed failure allowance (error budgets), and alerts based on the rate of budget consumption (burn rate) rather than arbitrary thresholds.

## Why it matters

Arbitrary alert thresholds create noise: they fire on transient spikes, miss slow-burning degradation, and have no connection to what "good" actually means for users. The result is alert fatigue — engineers stop responding. SLOs anchor reliability to user experience, error budgets make trade-offs concrete, and burn rate alerts fire when you're actually at risk.

## How it works

### SLI — what you're measuring

A **Service Level Indicator** is a ratio of good events to total events:

```
SLI = good requests / total requests
```

Not a raw count or average — a proportion. This normalizes for traffic volume: twice the errors at twice the traffic might still mean the same error rate.

Good SLIs measure things users actually experience: proportion of requests returning non-5xx responses, proportion completing under 500ms (see [[Metrics and Percentiles]]), proportion of background jobs finishing within their window.

### SLO — the target

A **Service Level Objective** is a target value for an SLI over a rolling time window.

- Standard window: **30 days** — sensitive enough to catch problems, stable enough to avoid being dominated by brief spikes
- Example: 99.5% of requests return non-5xx responses over the last 30 days

**Calibration:**
- Set too loose: SLO never approaches breach — you're leaving reliability signal on the table
- Set too tight: SLO is always on fire — no signal value, just noise
- For existing services: start at your 30-day baseline + ~20% headroom

### Error budget — the allowed failure

```
error budget = 1 - SLO
```

A 99.5% availability SLO means 0.5% of requests can fail — that's the budget.

Error budgets make reliability a shared resource. An aggressive feature rollout that destabilizes the service isn't just a technical problem — it's consuming budget. When budget is healthy, you have room to take risks. When it's running low, that's a signal to slow down.

### Burn rate — how fast you're spending it

```
burn rate = observed error rate / error budget rate
```

A burn rate of 1 = you'll exactly exhaust your budget by end of window.
A burn rate of 6 = you'll exhaust it in 5 days (30/6).
A burn rate of 14 = you'll exhaust it in ~2 days.
A burn rate of 100 during a full outage = you have hours.

### Alerting tiers

| Severity | Burn Rate | Measurement Window | Time to Exhaustion | Response |
|---|---|---|---|---|
| Minor | > 1 | 6 hours | Draining slowly | Next business day |
| Major | > 6 | 30 minutes | ~5 days | Within business hours |
| Critical | > 14 | 5 minutes | ~2 days | Page immediately |

Shorter windows for higher burn rates — at burn rate 14, you need to know fast. Shorter windows on low burn rates just produce noise from transient spikes.

### Worked examples

**Elevated error rate:** SLO = 99.5% (budget = 0.005). Current error rate = 2% (0.02). Burn rate = 0.02 / 0.005 = **4**. Budget exhausted in 7.5 days → Major alert.

**Slow latency degradation:** SLO = 90% of requests under 300ms (budget = 0.1 slow requests). Currently 20% exceeding threshold. Burn rate = 0.2 / 0.1 = **2**. 15 days to exhaustion → Minor alert.

**Full outage:** SLO = 99.5%, 50% of requests failing. Burn rate = 0.5 / 0.005 = **100**. Budget exhausted in 7.2 hours → Page immediately.

## Key tradeoffs

- **SLO tightness vs. engineering velocity** — tighter SLOs reduce error budget, leaving less room for risky deploys; this creates healthy pressure but can slow down teams that need to ship fast
- **Burn rate sensitivity vs. noise** — short measurement windows catch problems fast but false-alarm on transient spikes; longer windows reduce noise but delay detection; the tiered approach handles both
- **User-facing SLIs vs. infrastructure metrics** — CPU utilization doesn't directly tell you if users are having a bad time; SLIs should measure what users experience, not what's convenient to instrument
- **30-day rolling window vs. calendar month** — rolling windows give consistent behavior regardless of when a problem occurs; calendar months create discontinuities at month boundaries
