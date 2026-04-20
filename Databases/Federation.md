# Federation

Splitting a database by function or domain so that each node holds a different schema — users in one database, orders in another, products in a third — rather than splitting rows of the same table across nodes.

## Why it matters

A single monolithic database eventually becomes a bottleneck not just on storage or throughput, but on schema ownership and independent deployability. Federation assigns each domain to its own database instance, so teams can scale, deploy, and tune each database independently without coupling. It also reduces the blast radius of schema migrations and outages.

## How it works

Each federated database is a fully independent instance with its own schema, connection pool, and operational footprint. The application layer (or a service layer) is responsible for routing queries to the right database.

A typical split follows domain boundaries:

- `users_db` — accounts, profiles, authentication
- `orders_db` — orders, line items, fulfillment state
- `products_db` — catalog, inventory, pricing

Reads and writes that touch only one domain go directly to that database. Operations that span domains — e.g., look up a user and their recent orders — require multiple queries from the application and manual assembly of results.

Federation is sometimes called **functional partitioning** or **vertical sharding** (splitting by entity type rather than by row), though "federation" is the more common term in system design literature.

## Key tradeoffs

- **No cross-database joins** — joins across federated databases must be done in application code; this is complex and loses the query planner's ability to optimize
- **No cross-database transactions** — referential integrity across domains (e.g., an order referencing a valid user) cannot be enforced at the database level; requires application-level consistency or [distributed transactions](../Distributed%20Systems/Distributed%20Transactions.md)
- **Independent scaling** — each database can be sized, indexed, and tuned for its own workload without affecting others; a write-heavy orders DB can be scaled independently of a read-heavy products catalog
- **Schema isolation** — teams own their database schema with no risk of cross-domain coupling at the storage layer; migrations in one domain don't block others
- **Operational multiplication** — each federated database is a separate operational unit: separate backups, monitoring, failover configuration, and connection pools

## Related concepts

- [Sharding](Sharding.md) — sharding splits rows of the same schema across nodes; federation splits by entity type with different schemas per node
- [Partitioning](Partitioning.md) — partitioning divides a single table within one instance; federation divides ownership of entire schemas across instances
- [Distributed Transactions](../Distributed%20Systems/Distributed%20Transactions.md) — cross-domain writes in a federated system require distributed coordination to remain atomic
- [Replication](Replication.md) — each federated database is independently replicated for fault tolerance
- [Relational Databases](Relational%20Databases.md) — federation gives up relational integrity across domain boundaries in exchange for independence
