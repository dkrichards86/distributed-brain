# DynamoDB Hot Partitions

A condition where traffic concentrates on a single DynamoDB partition, causing throttling and latency despite adequate total provisioned capacity.

## Why it matters

DynamoDB splits capacity evenly across partitions. If most of your traffic hashes to one partition, that partition gets overwhelmed while the others sit idle. You can provision plenty of capacity at the table level and still get throttled — because the bottleneck is per-partition, not per-table.

## How it works

DynamoDB determines partition count from the larger of:

```
MAX(
  table size in GB / 10,
  (RCU / 3000) + (WCU / 1000)
)
```

Each item is placed on a partition by hashing its partition key. The hash function distributes randomly-distributed keys uniformly — but if your keys aren't random, skew survives the hash.

**Patterns that guarantee hot partitions:**

- **Sequential keys** (timestamps, auto-incrementing IDs) — all new writes hit the same partition
- **Low-cardinality keys** (`status`, `region`) — too few buckets for traffic to spread
- **Predictable access patterns** — high-traffic users all on the same partition even with high-cardinality keys
- **Time-based access** — recent data gets most reads, creating temporal hot spots

**Distribution strategies:**

| Strategy | Mechanism | Trade-off |
|---|---|---|
| UUID partition keys | Natural randomness | Lose meaningful ordering |
| Hash prefixes | Prepend a hash of the key | Preserves identifier, adds noise |
| Composite prefixes | `user_id + activity_type` | Splits one entity across partitions |
| Write sharding | Append random suffix (`key_0`–`key_9`) | Reads must scatter-gather across shards — see [DynamoDB Query Patterns](DynamoDB%20Query%20Patterns.md) |

**Detection:** Table-level CloudWatch metrics can show healthy utilization while a single partition is overwhelmed. `ThrottleEvents` despite low overall utilization = suspect hot partitions. DynamoDB **Contributor Insights** shows which partition keys receive the most traffic.

Partitions are never deleted or merged once created — traffic spikes permanently increase partition count.

## Key tradeoffs

- **Distribution vs. queryability** — UUID keys distribute perfectly but prevent range queries; grouping related items on the same partition enables efficient scans but risks hot spots for power users
- **Write sharding cost** — solves hot write partitions but requires scatter-gather on reads (query all shards, merge results)
- **On-demand billing** — absorbs hot partition traffic better than provisioned capacity since it autoscales; higher per-request cost but no risk of under-provisioning; see [DynamoDB Capacity Modes](DynamoDB%20Capacity%20Modes.md)
- **Load testing realism** — uniform random test traffic won't surface hot partitions from skewed production patterns; test with realistic access distributions

