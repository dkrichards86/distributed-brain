# MVCC (Multi-Version Concurrency Control)

A concurrency control technique where writes create new versions of rows rather than overwriting them in place, allowing readers and writers to operate simultaneously without blocking each other.

## Why it matters

The naive way to prevent a reader from seeing a half-written row is to lock it. But locking means reads block writes and writes block reads — a busy table becomes a bottleneck. MVCC eliminates this: readers always see a consistent snapshot of the database as of the moment their transaction started, regardless of what writers are doing concurrently. Writers don't block readers; readers don't block writers. This is why Postgres, MySQL InnoDB, Oracle, and CockroachDB all use MVCC.

## How it works

### Versions, not overwrites

When a transaction updates a row, the database doesn't modify the existing row. Instead, it writes a **new version** of the row with a transaction ID (or timestamp) indicating when it became valid. The old version remains, tagged with when it was superseded.

Example — updating a user's email:

```
Row versions (simplified):
  [txn_id: 100, email: "old@example.com", valid_from: 100, valid_to: 200]
  [txn_id: 200, email: "new@example.com", valid_from: 200, valid_to: ∞]
```

A transaction that started before txn 200 sees the old version. A transaction that started after sees the new one. Both are reading from their own consistent snapshot.

### Snapshot isolation

When a transaction starts, it gets a **snapshot** — effectively a point-in-time view of all committed data. Any rows written by transactions that committed after the snapshot was taken are invisible. Any rows written by transactions still in progress are also invisible.

This means:
- Long-running reads don't see writes that happen while they're running
- Writers creating new data don't interfere with concurrent readers
- The reader always sees a consistent, internally coherent state

### Deletes

Deletes work the same way — the row isn't physically removed. Its `valid_to` is set to the deleting transaction's ID. The row becomes invisible to newer snapshots but still exists on disk until cleanup.

### Vacuum / garbage collection

Old versions pile up. Postgres calls its cleanup process **VACUUM**; other databases have similar GC mechanisms. VACUUM removes row versions that are older than the oldest active transaction's snapshot — any version that no old transaction can still see is dead weight and can be reclaimed.

This creates an important operational concern: **long-running transactions hold back vacuum**. A transaction that's been open for hours prevents any row version older than its snapshot from being collected. On a busy table, this causes **table bloat** — the physical table file grows unboundedly as dead versions accumulate.

### MVCC and isolation levels

MVCC naturally provides **snapshot isolation** — transactions see a consistent point-in-time view. Most databases implement their SQL isolation levels on top of this:

| Isolation level | What it prevents |
|---|---|
| Read committed | Dirty reads (seeing uncommitted data) |
| Repeatable read | Non-repeatable reads (a row changing between two reads in one txn) |
| Snapshot isolation | Most anomalies; implemented via MVCC snapshots |
| Serializable | All anomalies including write skew; requires additional tracking |

Postgres's default isolation level is **read committed** — each statement in a transaction gets a fresh snapshot, so you can still see commits that happen between statements. Setting `REPEATABLE READ` or `SERIALIZABLE` locks the snapshot to the transaction start.

## Key tradeoffs

- **Bloat from old versions** — dead row versions accumulate between vacuum runs; high-churn tables require aggressive autovacuum tuning or they grow continuously
- **Long transactions block cleanup** — a transaction that stays open for hours prevents dead version reclamation; monitoring `pg_stat_activity` for long-running transactions is an operational necessity
- **Write-write conflicts** — MVCC handles read-write concurrency cleanly, but two writers updating the same row still require conflict detection; Postgres uses a "first writer wins" rule and aborts the second transaction
- **Snapshot overhead** — maintaining version metadata per row adds storage cost; wide tables with many frequent updates accumulate more dead weight than append-only or rarely-updated tables

## Related concepts

- [Relational Databases](Relational%20Databases.md) — Postgres and MySQL InnoDB both use MVCC as their core concurrency mechanism
- [Consistency Models](Consistency%20Models.md) — MVCC implements snapshot isolation on a single node; distributed consistency models address the same problem across nodes
- [Write-Ahead Logging](Write-Ahead%20Logging.md) — MVCC writes are recorded in the WAL before being applied, tying version management to crash recovery
