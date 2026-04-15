# DynamoDB Operation Semantics

The set of API operations DynamoDB provides for reading and writing items, and when to use each one.

## Why it matters

Choosing the wrong operation costs money, causes throttling, or silently corrupts data. `Scan` on a large table is a common foot-gun. `PutItem` vs `UpdateItem` is a subtle correctness issue that can wipe attributes if used carelessly.

## How it works

### Read operations

| Operation | What it does | Key constraint |
|---|---|---|
| **GetItem** | Fetch a single item by full primary key (PK + SK) | Exact match only — no conditions |
| **Query** | Fetch multiple items sharing a PK, optionally filtered by SK condition | Requires PK; SK condition optional |
| **Scan** | Read every item in the table or index | No key required — full table read |

**GetItem** is the cheapest and fastest read. Always prefer it when you have the full key.

**Query** operates within a single partition. You supply the exact PK and an optional SK expression (`begins_with`, `between`, `=`, `<`, `>`, `<=`, `>=`). A `FilterExpression` can narrow results further but filtering happens *after* items are read — you still pay for and receive the full 1MB page before filtering.

**Scan** reads every item sequentially across all partitions. Useful for backfills, migrations, and analytics on small tables. On large tables it's slow, expensive, and can consume your full provisioned throughput. Parallel scan (divide table into segments, scan concurrently) speeds it up but doesn't reduce cost.

**Consistency options** (GetItem and Query) — see [Consistency Models](../Consistency%20Models.md):
- `ConsistentRead: false` (default) — eventually consistent, half the read capacity cost
- `ConsistentRead: true` — strongly consistent, full read capacity cost; not available on GSIs

---

### Write operations

| Operation | What it does | Key behavior |
|---|---|---|
| **PutItem** | Write a complete item | Replaces the entire item if it exists |
| **UpdateItem** | Modify specific attributes | Merges changes; unmentioned attributes are untouched |
| **DeleteItem** | Remove an item by full key | Optionally conditional |

**PutItem** is a full replace. If you read an item, modify one field in your application, then PutItem the whole object back, you lose any attributes written by a concurrent process. Safe when you own the full item shape or are creating new items.

**UpdateItem** is a partial update. You supply an `UpdateExpression` targeting specific attributes (`SET`, `REMOVE`, `ADD`, `DELETE`). The item is created if it doesn't exist (upsert). Use this for counters, appending to sets, or any case where concurrent writers might touch different attributes.

**Conditional writes** — both PutItem, UpdateItem, and DeleteItem accept a `ConditionExpression`. If the condition fails, the operation is rejected with `ConditionalCheckFailedException`. This is DynamoDB's optimistic locking primitive.

---

### Batch and transaction operations

| Operation | Limit | Behavior on partial failure |
|---|---|---|
| **BatchGetItem** | 100 items, 16MB | Unprocessed keys returned — you must retry |
| **BatchWriteItem** | 25 items, 16MB | Unprocessed items returned — you must retry; no UpdateItem support |
| **TransactGetItems** | 100 items | All-or-nothing read; 2x read cost |
| **TransactWriteItems** | 100 items | All-or-nothing write; 2x write cost |

**Batch operations** are not atomic. They're a network efficiency optimization — DynamoDB processes each item independently and returns failures in an `UnprocessedKeys`/`UnprocessedItems` list. Your code must implement retry logic. `BatchWriteItem` only supports PutItem and DeleteItem, not UpdateItem.

**Transact operations** are atomic across up to 100 items and multiple tables. A failure on any item rolls back the entire transaction. The 2x cost comes from DynamoDB writing a transaction journal entry. Use transactions for things like: decrement inventory and create an order record atomically, or conditional multi-item consistency checks.

---

### UpdateExpression operators

| Operator | Use case |
|---|---|
| `SET` | Set or overwrite an attribute |
| `REMOVE` | Delete an attribute or list element |
| `ADD` | Increment a number or add to a set |
| `DELETE` | Remove elements from a set |

## Key tradeoffs

- **PutItem simplicity vs. safety** — PutItem is easier to reason about but dangerous under concurrent writes; UpdateItem is safer but requires learning expression syntax
- **Batch cost vs. atomicity** — BatchWriteItem is cheap and fast but not atomic; TransactWriteItems is atomic but 2x cost and stricter limits
- **FilterExpression illusion** — looks like server-side filtering but you pay for all items read before the filter; for high-cardinality filtering, a [GSI](DynamoDB%20Indexes.md) is almost always better
- **Scan throughput impact** — a full scan on a provisioned table can consume 100% of read capacity and starve real traffic; use `--page-size` and throttle with `ReturnConsumedCapacity`
- **Capacity mode matters** — the RCU/WCU costs above apply in both modes; see [DynamoDB Capacity Modes](DynamoDB%20Capacity%20Modes.md) for how provisioned vs. on-demand affects throttling behavior
