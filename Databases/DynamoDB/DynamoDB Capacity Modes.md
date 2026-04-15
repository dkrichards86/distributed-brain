# DynamoDB Capacity Modes

The two billing and throughput models for DynamoDB tables: **provisioned** (you declare RCU/WCU limits upfront and pay for them) and **on-demand** (DynamoDB scales automatically and you pay per request).

## Why it matters

Every DynamoDB read and write consumes capacity. If you exceed your provisioned limits — even briefly — requests are throttled with `ProvisionedThroughputExceededException`. Choosing the wrong capacity mode means either paying for idle capacity or getting throttled on spikes. The choice also affects how you think about [hot partitions](DynamoDB%20Hot%20Partitions.md), [autoscaling](DynamoDB%20Autoscaling.md), and cost predictability.

## How it works

### Capacity units

The fundamental billing unit applies in both modes:

| Unit | What it covers |
|---|---|
| **1 RCU** | 1 strongly consistent read/sec of up to 4KB, or 2 eventually consistent reads/sec of up to 4KB |
| **1 WCU** | 1 write/sec of up to 1KB |
| **Transactional reads** | 2 RCUs per 4KB (double the standard rate) |
| **Transactional writes** | 2 WCUs per 1KB (double the standard rate) |

For items larger than the base size, cost scales linearly: a 10KB item costs `ceil(10/4) = 3` RCUs per strongly consistent read and `ceil(10/1) = 10` WCUs per write.

---

### Provisioned mode

You declare a fixed number of RCUs and WCUs per table (and per index). DynamoDB enforces these limits per second, per partition. You pay for the provisioned amounts whether or not you use them.

**Burst capacity:** DynamoDB accumulates up to 5 minutes (300 seconds) of unused partition-level capacity as burst. This absorbs momentary spikes above the provisioned rate without throttling — but burst is not guaranteed; background processes can consume it, and it doesn't extend beyond 300 seconds of accumulated headroom.

**Adaptive capacity:** When traffic concentrates on a hot partition, DynamoDB automatically shifts capacity from under-utilized partitions to the hot one — up to the table's total provisioned capacity. Adaptive capacity takes a few minutes to respond and cannot exceed the table-level limit; it only rebalances within it.

**When to use provisioned:**
- Traffic is predictable or follows a known schedule
- Cost optimization matters and you can model expected throughput
- You want hard cost caps (no per-request surprises)
- You're using [autoscaling](DynamoDB%20Autoscaling.md) to adjust capacity automatically

---

### On-demand mode

DynamoDB serves any request volume up to the table's previous peak (doubled). You pay per request rather than for provisioned capacity. There are no limits to configure — the table scales transparently.

**Previous peak limit:** on-demand tables are pre-warmed to 2× their previous traffic peak. If traffic exceeds this (e.g., a table is newly created and immediately hit with a large load), DynamoDB scales up but may throttle for a brief window while it provisions additional capacity. The table's peak high-water mark resets daily.

**When to use on-demand:**
- Traffic is unpredictable or spiky (new tables, event-driven workloads, dev/test)
- You can't accurately forecast capacity
- Operational simplicity matters more than cost optimization
- Per-request cost is acceptable (on-demand is typically 6–7× more expensive per million requests than right-sized provisioned)

---

### Mode switching

You can switch a table between provisioned and on-demand once every 24 hours. Switching to on-demand pre-warms the table to its previous provisioned capacity, so switching just before an anticipated spike is a valid strategy.

## Key tradeoffs

- **Cost vs. risk** — provisioned is cheaper per request when traffic is predictable but you pay for idle capacity and risk throttling on unexpected spikes; on-demand eliminates throttling risk at a higher per-request cost
- **Hot partition behavior** — on-demand handles [hot partitions](DynamoDB%20Hot%20Partitions.md) more gracefully because DynamoDB manages the scaling; provisioned mode throttles hot partitions even if total table utilization is low
- **Capacity planning overhead** — provisioned mode requires ongoing capacity monitoring and adjustment (or [autoscaling](DynamoDB%20Autoscaling.md)); on-demand removes this operational burden
- **Burst ceiling** — provisioned burst capacity is bounded at 5 minutes of accumulated headroom per partition; on-demand can absorb larger sustained spikes but still has a previous-peak limit

## Related concepts

- [DynamoDB Autoscaling](DynamoDB%20Autoscaling.md) — automates capacity adjustments for provisioned tables; bridges the gap between manual provisioning and on-demand
- [DynamoDB Hot Partitions](DynamoDB%20Hot%20Partitions.md) — capacity mode significantly affects throttling behavior under skewed traffic; on-demand is more resilient to hot partitions
- [DynamoDB Operation Semantics](DynamoDB%20Operation%20Semantics.md) — the RCU/WCU cost of each operation type (consistent reads, transactions, scans) determines how capacity is consumed
