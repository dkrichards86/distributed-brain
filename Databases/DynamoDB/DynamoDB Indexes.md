# DynamoDB Indexes

Secondary indexes that provide alternative views of a DynamoDB table's data, enabling access patterns the base table's primary key can't support.

## Why it matters

The primary key design locks you into specific query shapes. If you partition by `user_id` and later need to find users by email, the base table has no efficient path to that query. Indexes let you project the same data under different keys without duplicating data management logic in your application.

## How it works

### Local Secondary Index (LSI)

Shares the base table's partition key but uses a different sort key. Items with the same partition key stay on the same physical partition — hence "local."

- **Use when:** You need multiple sort orders within the same partition (e.g. query a user's orders by date *and* by status)
- **Consistency:** Supports strongly consistent reads
- **Throughput:** Shares capacity with the base table — no extra provisioning
- **Hard constraint:** Must be defined at table creation time. Cannot be added later.
- **Size limit:** All items sharing a partition key value, across base table + all LSIs combined, cannot exceed 10 GB

---

### Global Secondary Index (GSI)

Completely independent partition and sort keys — no relation to the base table's keys. DynamoDB maintains it as a separate internal table and updates it asynchronously on writes.

- **Use when:** You need to query across different partition keys, or you discover a new access pattern after the table exists
- **Consistency:** Eventually consistent only (GSI replication is async) — no strongly consistent reads
- **Throughput:** Has its own provisioned or on-demand capacity, billed separately
- **Flexibility:** Can be added or removed at any time

---

### LSI vs. GSI at a glance

| | LSI | GSI |
|---|---|---|
| Partition key | Same as base table | Any attribute |
| Sort key | Different from base table | Any attribute |
| Consistency | Strong or eventual | Eventual only |
| Throughput | Shared with base table | Separate |
| Add after creation | No | Yes |
| Size limit per PK | 10 GB | None |

---

### Projection

Both index types require a projection — which attributes are copied into the index.

| Projection | What's stored | Trade-off |
|---|---|---|
| **Keys only** | PK + SK of base table and index | Cheapest; must fetch full item from base table for other attributes |
| **Include** | Keys + specific named attributes | Sweet spot; include what your queries need, skip the rest |
| **All** | Every attribute | Most expensive; queries never need a base table fetch |

If a query needs an attribute not in the projection, DynamoDB transparently fetches it from the base table (a hidden [[DynamoDB Operation Semantics|GetItem]]) — but this adds latency and consumes base table read capacity. Design projections to avoid this on hot paths.

---

### Sparse indexes

If an item doesn't have the GSI's partition or sort key attribute, it's excluded from the index entirely. This creates a filtered view without a separate table.

Example: a table of all orders where 10% are flagged for review. Set a `needs_review` attribute only on flagged orders and use it as the GSI partition key. The GSI contains only the 10% of items you care about — cheaper to query and smaller to store. See [[DynamoDB Query Patterns]] for how sparse GSIs fit into single-table design.

---

### Write amplification

Every write to the base table that touches an indexed attribute triggers a write to each GSI containing that attribute. Three GSIs on an updated item = four total writes. This multiplies write costs and can become a meaningful throughput and cost factor with many indexes.

---

### Capacity and billing

- **Provisioned mode:** Each GSI needs its own RCU/WCU allocation. Under-provisioning a GSI throttles index reads/writes independently of the base table.
- **On-demand mode:** GSIs scale automatically with the table. Often simpler and cheaper when traffic is unpredictable or you have many GSIs.
- **LSIs:** No separate capacity — billed through the base table. Still consume write capacity on every relevant write.

## Key tradeoffs

- **LSI immutability** — strong consistency and no extra capacity cost, but you're locked in at creation; an unplanned access pattern means no LSI option
- **GSI eventual consistency** — maximum flexibility and can be added anytime, but you can't do strongly consistent reads; a brief replication lag exists after every write
- **Projection size vs. query cost** — larger projections increase storage and write costs but eliminate base table fetches on reads; smaller projections save money at rest but add latency on non-projected attribute access
- **Index count vs. write cost** — more indexes = more access patterns supported, but write amplification grows linearly; every index has to pay its way
