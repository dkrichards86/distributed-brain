# DynamoDB Autoscaling

An AWS Application Auto Scaling integration that automatically adjusts a DynamoDB table's provisioned RCU and WCU in response to observed traffic, targeting a configured utilization percentage.

## Why it matters

Manually managing provisioned capacity is operationally expensive and error-prone — you either over-provision (wasteful) or under-provision (throttling). Autoscaling removes the need to predict traffic precisely: you set a utilization target and capacity bounds, and the system adjusts within those bounds automatically. It's the practical middle ground between manual provisioned capacity and fully automatic [on-demand mode](DynamoDB%20Capacity%20Modes.md).

## How it works

### Target tracking policy

Autoscaling uses a **target tracking** policy: you declare a target consumed-capacity utilization percentage (default 70%), and the system continuously adjusts provisioned capacity to keep actual consumption near that target.

The 70% default provides a buffer — if you're consuming 70% of provisioned capacity, you have 30% headroom before throttling, while still not paying for large idle reserves.

### Scale-out

When consumed capacity exceeds the target utilization for a sustained period (~2 minutes), autoscaling increases provisioned capacity. Scale-out is aggressive by design — the system overshoots slightly to absorb the load quickly.

DynamoDB itself imposes a limit on how fast provisioned capacity can grow: each table can be increased by at most the larger of 3,000 RCUs or 1,000 WCUs per minute, and the table cannot be scaled more than twice in a 15-minute window (unless scaling up, which has fewer restrictions).

### Scale-in

Scale-in is conservative. Autoscaling waits until utilization has been below the target for a sustained period (**scale-in cooldown**, default 15 minutes) before reducing capacity. This prevents oscillation — scaling down immediately after a spike would trigger another scale-out on the next spike.

### Minimum and maximum capacity

You set hard bounds:
- **Minimum capacity** — the floor; capacity never drops below this even at zero traffic; set high enough to absorb the fastest expected traffic ramp
- **Maximum capacity** — the ceiling; a cost guard; capacity never exceeds this even under heavy load; if traffic exceeds maximum × target utilization, throttling occurs

Setting max capacity too low is the most common autoscaling misconfiguration — the table is protected from cost surprises but throttles under legitimate spikes.

### Index autoscaling

Autoscaling is configured **per table and per index independently**. GSI capacity is separate from base table capacity. If your access pattern shifts traffic heavily to a GSI, the GSI must have its own autoscaling configuration — the table's autoscaling does not cover its indexes automatically. When you enable autoscaling on a table via the console, it applies to the table and all existing GSIs by default, but new GSIs must be configured separately.

### What autoscaling cannot do

- **React to sudden spikes** — autoscaling has a ~2-minute reaction lag; a traffic spike that doubles load instantly will cause throttling until autoscaling catches up. [Burst capacity](DynamoDB%20Capacity%20Modes.md) absorbs the initial window, but sustained spikes will throttle before autoscaling responds.
- **Scale beyond the maximum** — if traffic exceeds `max_capacity × target_utilization`, requests throttle regardless of demand
- **Handle per-partition hot spots** — autoscaling adjusts table-level capacity; [hot partitions](DynamoDB%20Hot%20Partitions.md) can throttle even when the table is well within its autoscaled limits

### Autoscaling vs. on-demand

| | Autoscaling (provisioned) | On-demand |
|---|---|---|
| Reaction to spikes | ~2 minutes lag | Instant (up to 2× previous peak) |
| Cost at steady traffic | Lower (right-sized provisioned rate) | Higher (per-request pricing) |
| Cost at idle | Minimum capacity charge | Zero (no requests = no cost) |
| Hot partition resilience | Partial (table-level only) | Better |
| Operational overhead | Low (set and forget) | Zero |

A common pattern: use on-demand for new tables or unpredictable workloads, then switch to provisioned + autoscaling once traffic patterns stabilize and the provisioned cost savings justify it.

## Key tradeoffs

- **Reaction lag vs. cost** — autoscaling's ~2-minute lag means sudden spikes always cause some throttling; the alternative (on-demand) eliminates throttling but costs more per request at steady state
- **Min capacity sizing** — a min capacity that's too low means cold tables take time to scale up after idle periods; too high wastes money during off-peak hours
- **Max capacity as a cost guard** — max capacity protects against runaway costs but becomes a throttle ceiling; it must be set with awareness of peak expected traffic
- **GSI blindspot** — forgetting to configure autoscaling on GSIs is a frequent cause of GSI throttling that looks puzzling when the base table utilization appears healthy

## Related concepts

- [DynamoDB Capacity Modes](DynamoDB%20Capacity%20Modes.md) — autoscaling only applies to provisioned mode; on-demand is the alternative when autoscaling's reaction lag is unacceptable
- [DynamoDB Hot Partitions](DynamoDB%20Hot%20Partitions.md) — autoscaling adjusts table-level capacity but cannot fix hot partition throttling; both problems can coexist
- [DynamoDB Indexes](DynamoDB%20Indexes.md) — GSIs have independent capacity; autoscaling must be configured on each index separately
