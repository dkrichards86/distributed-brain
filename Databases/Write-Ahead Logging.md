# Write-Ahead Logging

A durability technique where every change is written to an append-only log on disk before being applied to the actual data files.

## Why it matters

Database pages live in memory (the buffer pool / page cache) and are flushed to disk lazily — flushing on every write would be too slow. But if the process crashes before modified pages are flushed, those changes are lost. WAL solves this: by persisting the *intent* of a change before applying it, the database can reconstruct any in-flight operation after a crash by replaying the log. You get the performance of buffered, asynchronous writes to data files with the durability of synchronous writes.

## How it works

### The write path

1. A transaction's changes are described as log records and appended to the WAL file
2. The WAL write is flushed (fsync'd) to disk — this is the durability guarantee
3. The transaction is acknowledged to the client
4. The actual data pages in the buffer pool are modified in memory
5. Those pages are flushed to the data files asynchronously in the background

The key invariant: **log record must hit durable storage before the transaction is confirmed.** The data file write can happen later.

### Crash recovery

On restart after a crash:
1. Find the last **checkpoint** — a point where all dirty pages were known to have been flushed
2. **Redo** all committed transactions that appear in the log after the checkpoint (their page writes may not have landed)
3. **Undo** any transactions that were in-progress at the time of the crash (they were never committed)

This is why Postgres calls its WAL recovery a "redo" pass — committed changes are replayed; uncommitted ones are rolled back.

### WAL as a replication stream

The WAL contains a complete record of every change to the database, in order. This makes it a natural replication feed — Postgres logical and physical replication both work by streaming the WAL to replicas. The replica applies the same log records, arriving at an identical state.

### Group commit

Flushing the WAL (fsync) for every single transaction would serialize all writers. **Group commit** batches multiple transactions' log records into a single fsync, amortizing the disk latency across concurrent writers. This is why Postgres's `commit_delay` and `wal_writer_delay` parameters exist.

## Key tradeoffs

- **Write amplification** — every change is written twice: once to the WAL, once to the data file; on top of this, [LSM trees](LSM%20Trees.md) use their own WAL in addition to their SSTable writes
- **fsync latency** — the WAL fsync is on the critical path for transaction commit latency; slow disks or misconfigured `fsync=off` (dangerous) directly affect write throughput
- **WAL size and retention** — WAL files must be retained until all replicas and backups have consumed them; a lagging replica holds back WAL deletion, growing disk usage
- **`fsync=off` risk** — disabling fsync on the WAL removes the durability guarantee entirely; the database will report successful commits that can be lost on a crash; used only in bulk load scenarios where data can be reloaded

## Related concepts

- [Relational Databases](Relational%20Databases.md) — Postgres and MySQL both use WAL for transaction durability
- [LSM Trees](LSM%20Trees.md) — also use a WAL to make MemTable writes durable before the flush to SSTable
- [Replication](Replication.md) — Postgres streaming replication works by shipping WAL records to replicas
- [Event Sourcing](../Architecture/Event%20Sourcing.md) — applies the same append-only log principle at the application domain level; the event log is to the application what the WAL is to the database
