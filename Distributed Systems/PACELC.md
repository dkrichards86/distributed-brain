# PACELC

An extension of the [CAP theorem](CAP%20Theorem.md) that adds a second tradeoff: even when a distributed system is healthy (no partition), it must choose between lower latency and stronger consistency.

## Why it matters

CAP only describes behavior during a network partition — a relatively rare event. PACELC fills the gap: in normal operation, every replication system still faces a choice between waiting for replicas to confirm a write (higher consistency, higher latency) and acknowledging immediately (lower latency, possible staleness). This is the tradeoff engineers tune day-to-day, making PACELC more practically useful than CAP for system design.

## How it works

The name encodes both tradeoffs:

- **PAC** — during a **P**artition: choose between **A**vailability and **C**onsistency (identical to CAP)
- **ELC** — **E**lse (normal operation): choose between **L**atency and **C**onsistency

In the ELC dimension, the question is: how many replicas must acknowledge a write before the system returns success to the caller?

- **Favor latency** — acknowledge after writing to one node (or even before any replica confirms); reads may return stale data
- **Favor consistency** — wait for a quorum or all replicas to confirm; every read sees the latest write, but write latency includes the slowest replica's round-trip

Most production systems make this configurable per-request:

| System    | Latency-favoring         | Consistency-favoring                 |
| --------- | ------------------------ | ------------------------------------ |
| DynamoDB  | Default reads (eventual) | `ConsistentRead: true`               |
| Cassandra | `ONE` consistency level  | `QUORUM` or `ALL`                    |
| MongoDB   | Default writes           | `writeConcern: majority`             |
| Spanner   | —                        | Always consistent (pays the latency) |

## Key tradeoffs

- **The ELC tradeoff is always present** — even on a single-region cluster with no partitions, async replication means replicas lag; synchronous replication adds latency to every write
- **Geo-distribution amplifies it** — cross-region replication adds 50–200ms of WAN latency; waiting for a cross-region quorum is often unacceptable, so most geo-distributed systems favor latency by default
- **Tunability is not free** — per-request consistency levels require the application to reason about which operations need strong consistency; the wrong default causes subtle, hard-to-reproduce staleness bugs

## Related concepts

- [CAP Theorem](CAP%20Theorem.md) — the partition-time tradeoff that PACELC extends; PACELC's PAC half is identical to CAP
- [Consistency Models](../Databases/Consistency%20Models.md) — the full spectrum of consistency guarantees; PACELC's L/C axis maps onto this spectrum
- [Replication](../Databases/Replication.md) — synchronous vs. asynchronous replication is the mechanical implementation of the PACELC latency/consistency dial
