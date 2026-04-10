# Consistency Models

Formal guarantees about which version of data a distributed system promises to return after a write.

## Why it matters

When data is replicated across multiple nodes, there's always a window where different nodes have different views of the state. A write lands on the primary; the replicas haven't caught up yet. Does a read from a replica return the new value or the old one? The answer depends on the consistency model. Picking the wrong model means either building unnecessary coordination overhead into a system that doesn't need it, or silently serving stale data in a system that can't tolerate it.

## How it works

Models are ordered from strongest (most coordination required) to weakest (most available):

### Strong consistency (linearizability)

Every read reflects the most recent completed write, regardless of which node handles the request. The system behaves as if there's a single copy of the data.

- Requires coordination on every read or write to confirm no concurrent operation is in flight
- High latency; availability suffers during network partitions (see CAP theorem below)
- Used by: single-node databases, DynamoDB with `ConsistentRead: true`, Spanner

### Read-your-writes

A client always sees its own writes. Other clients may still see stale data.

- Weaker than strong consistency but sufficient for most user-facing apps (a user shouldn't see their profile revert after saving it)
- Typically implemented by routing a user's reads to the same replica they wrote to, or by using version tokens

### Monotonic reads

A client never observes data going "backwards" — if you read version 5, all subsequent reads return version ≥ 5.

- Prevents confusing UX where a page reload shows older data than the previous load
- Implemented by sticking a client to one replica or tracking a minimum version per session

### Causal consistency

Operations that have a cause-and-effect relationship are seen by all nodes in order. Unrelated operations can appear in any order.

- Example: if Alice posts a comment and Bob replies to it, any observer who sees Bob's reply must also see Alice's post
- Weaker than strong consistency but stronger than eventual; no global coordination needed, only tracking of causal dependencies (vector clocks)

### Eventual consistency

Given no new writes, all replicas will eventually converge to the same value. No timing guarantee on when.

- No coordination overhead; maximum availability and low latency
- The application must tolerate reading stale data
- Used by: DynamoDB default reads, DNS, most NoSQL databases at their default settings

---

### CAP theorem

A distributed system can provide at most two of three properties during a network partition:

- **Consistency** (every read returns the most recent write)
- **Availability** (every request receives a response)
- **Partition tolerance** (the system continues operating if nodes can't communicate)

Since network partitions are unavoidable in practice, the real choice is between **CP** (refuse reads/writes to avoid serving stale data) and **AP** (serve stale data to stay available). Most systems expose this as a tunable — DynamoDB's `ConsistentRead` flag is exactly this knob.

---

### PACELC

An extension of CAP for the non-partition case: even when the network is healthy, there's a tradeoff between **latency** and **consistency**. Lower latency means not waiting for all replicas to confirm; higher consistency means waiting longer. DynamoDB, Cassandra, and most distributed stores let you configure this per-operation.

## Key tradeoffs

- **Consistency vs. latency** — strong consistency requires a round-trip to confirm no concurrent writes; every step down the model reduces coordination and latency
- **Consistency vs. availability** — during a partition, a strongly consistent system must refuse requests rather than serve stale data; eventual consistency keeps serving requests but may return old values
- **Model vs. application complexity** — weaker models push conflict resolution to the application; strong consistency keeps that logic in the database at the cost of performance

## Related concepts

- [Replication](Replication.md) — the mechanism that creates the consistency problem; replicas diverge during replication lag
- [MVCC](MVCC.md) — how single-node databases achieve read isolation without sacrificing write throughput
- [DynamoDB Operation Semantics](DynamoDB/DynamoDB%20Operation%20Semantics.md) — DynamoDB's `ConsistentRead` flag exposes the CP/AP tradeoff directly
