# Distributed Transactions

Protocols for executing a transaction that spans multiple nodes or services atomically — either all operations commit or all roll back.

## Why it matters

A single-node database can wrap operations in a local transaction. Once data is partitioned across multiple nodes or owned by separate services, atomicity becomes a coordination problem. Without a distributed transaction protocol, a partial failure (one node commits, another crashes before it can) leaves the system in an inconsistent state with no automatic recovery path.

## How it works

### Two-phase commit (2PC)

The classic protocol. A **coordinator** manages the transaction across **participants**.

**Phase 1 — Prepare:**
- Coordinator sends `PREPARE` to all participants
- Each participant durably logs the transaction and replies `YES` (I can commit) or `NO` (I cannot)

**Phase 2 — Commit or abort:**
- If all replied `YES`: coordinator sends `COMMIT` to all participants and logs the decision
- If any replied `NO` or timed out: coordinator sends `ABORT`

**The problem — coordinator failure:** if the coordinator crashes after participants have voted `YES` but before sending the commit decision, participants are stuck in an uncertain state — they've reserved resources and can't unilaterally decide. This is the **blocking problem** of 2PC. Recovery requires the coordinator to come back or a new coordinator to be elected (which requires consensus).

### Three-phase commit (3PC)

Adds a `PRE-COMMIT` phase between prepare and commit. Participants that receive `PRE-COMMIT` know a commit decision was reached, so they can safely commit even if the coordinator disappears. This makes 3PC **non-blocking** — participants can always make progress.

The catch: 3PC is not safe under network partitions. A partitioned participant that received `PRE-COMMIT` might commit while the rest of the cluster aborts. In practice, 3PC is rarely used; real systems prefer 2PC with consensus-based coordinators (Percolator, Spanner) instead.

### Saga pattern

An alternative for microservice architectures that avoids distributed locking entirely. A saga breaks a transaction into a sequence of **local transactions**, each with a corresponding **compensating transaction** that undoes its effect.

- If all local transactions succeed: done
- If any step fails: execute compensating transactions in reverse order to undo completed steps

**Choreography:** each service publishes events and subscribes to others; no central coordinator.

**Orchestration:** a saga orchestrator drives the sequence, calling services and invoking compensations on failure.

Sagas are **not atomic** in the traditional sense — other transactions can observe intermediate state during saga execution. They work best for long-running business processes (order fulfillment, payment + inventory) where strict isolation is not required and compensating logic is business-meaningful.

## Key tradeoffs

- **2PC correctness vs. blocking** — 2PC is safe (ACID) but blocks if the coordinator fails mid-transaction; mitigated by running the coordinator on a consensus-backed system (etcd, Raft log)
- **3PC vs. partition safety** — 3PC avoids blocking but can produce incorrect results during network partitions; not usable in partition-prone environments
- **Sagas vs. isolation** — sagas avoid cross-service locking and are highly available, but intermediate state is visible; applications must tolerate or handle this (idempotency, compensating logic complexity)
- **Latency** — 2PC requires multiple round-trips across nodes; in geo-distributed systems this is expensive; Spanner uses TrueTime to minimize coordination rounds

## Related concepts

- [Consensus Algorithms](Consensus%20Algorithms.md) — a consensus-backed coordinator eliminates 2PC's blocking problem; Spanner and CockroachDB use Paxos/Raft for this
- [CAP Theorem](CAP%20Theorem.md) — 2PC is CP: it sacrifices availability (blocks) to maintain consistency
- [Sharding](../Databases/Sharding.md) — distributed transactions become necessary when data is sharded across nodes
- [Logical Clocks](Logical%20Clocks.md) — ordering events across transaction participants is a core requirement; Spanner uses physical clock bounds; others use logical timestamps
- [Delivery Semantics](../Messaging/Delivery%20Semantics.md) — exactly-once message processing is related; sagas in message-driven systems rely on idempotent handlers and at-least-once delivery
