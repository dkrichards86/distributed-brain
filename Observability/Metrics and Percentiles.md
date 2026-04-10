# Metrics and Percentiles

Quantitative measurements of system behavior, and the statistical techniques for interpreting them accurately.

## Why it matters

Averages lie. A response time average of 444ms can hide that four out of five requests were under 60ms and one outlier was 2000ms. Poor metric interpretation leads to teams building beautiful dashboards that don't drive good decisions — or missing slow-burning problems entirely.

## How it works

### Percentiles

A percentile Pn means "n% of observations fell below this value."

| Percentile | Use case | Sensitivity |
|---|---|---|
| **P50** (median) | Typical user experience | Low — not affected by outliers |
| **P90** | SLA targets and alerting | Good balance — catches meaningful degradation |
| **P99** | Worst-case / tail latency | High — a single slow request spikes this |
| **P99.9+** | Absolute worst case | Too noisy for day-to-day monitoring |

P90 is the sweet spot for most alerting. P99 is useful for understanding tail latency and tracking improvement over time, but bad for alerting thresholds due to outlier sensitivity.

### Aggregation windows

The window size determines what you see:

- **Short windows (1–5 min):** Reveal spikes and brief outages; noisy, prone to false alarms
- **Medium windows (1 hour):** Operational dashboards; smooths transients, still shows incidents
- **Long windows (daily/weekly):** Capacity planning and trend analysis; good for seasonality

**Counterintuitive:** A longer window produces a *lower* P99 than a short window over the same incident, because a 2-minute outage's bad requests are diluted across a full hour of traffic.

**Solution:** Layer windows — short for alerting, medium for dashboards, long for planning.

### Rates vs. counts

Error count increasing doesn't mean the system is degrading if traffic is also increasing. Always consider the denominator:

- **Error rate** (errors / total requests) = system health signal
- **Error count** = absolute impact signal

Both matter, for different decisions.

### Seasonality

A 20% response time increase on Tuesday afternoon is alarming. The same increase on Black Friday might be normal. Week-over-week comparisons often work better than hour-over-hour for business applications because they account for weekly cycles.

### What to measure

Good metrics correlate with outcomes: response time → conversion and retention, error rate → support load, CPU utilization → capacity headroom. Vanity metrics (server count, lines of code) look impressive on dashboards but don't drive decisions.

## Key tradeoffs

- **Short windows vs. noise** — catching problems fast vs. paging on-call for transient spikes
- **Average vs. percentile** — averages are intuitive but masked by outliers; percentiles are more complex but more honest about user experience
- **P90 vs. P99 for [SLAs](SLOs%20and%20Error%20Budgets.md)** — P90 is stable and actionable; P99 is more representative of real worst-case experience but harder to hold as a firm target
- **More metrics vs. cognitive load** — collecting everything is easy; knowing which metrics to watch during an incident requires deliberate curation
