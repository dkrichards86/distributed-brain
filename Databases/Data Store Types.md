# Data Store Types

The major categories of data storage systems, each optimized for a different access pattern or workload.

## Why it matters

No single data store is best at everything. Choosing the wrong one means trading correctness for speed, or paying massive query costs for workloads the store wasn't built for. Understanding the categories lets you match the tool to the job — and build polyglot architectures where each store does what it does best.

## How it works

### Relational databases

See [Relational Databases](Relational%20Databases.md)

---

### Document databases

See [Document Databases](Document%20Databases.md)

---

### Key-value databases

See [Key-Value Databases](Key-Value%20Databases.md)

---

### Columnar databases

See [Columnar Databases](Columnar%20Databases.md)

---

### Search databases

See [Search Databases](Search%20Databases.md)

---

### Analytical databases (data warehouses)

See [Analytical Databases](Analytical%20Databases.md)

---

### Object / blob storage

See [Object Storage](Object%20Storage.md)

---

### Decision heuristic

| Need | Reach for |
|---|---|
| Transactions + complex relationships | Relational |
| Evolving schema, fast iteration | Document |
| Pure speed, known access patterns | Key-value |
| Analytics over huge datasets | Columnar or Analytical |
| Full-text search with ranking | Search |
| Files, images, backups, data lake | Object storage |

Polyglot persistence — using multiple stores in one system, each for what it does best — is common in production architectures.

## Key tradeoffs

- **Flexibility vs. queryability** — schema-free stores (document, key-value) are easy to write to but hard to query across; relational schemas are rigid but queryable from any angle
- **Consistency vs. scale** — ACID relational stores are consistent but hard to scale horizontally; most NoSQL stores trade consistency guarantees for partition tolerance and throughput
- **Write vs. read optimization** — row-oriented stores (relational, document) are fast for single-record writes and reads; columnar stores are fast for aggregate reads but slow for point writes
- **Operational complexity** — polyglot persistence gives you best-in-class performance per use case but multiplies infrastructure, expertise, and consistency management costs
