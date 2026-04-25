# Stateless and Stateful Services

A stateless service holds no per-request or per-session data between calls; a stateful service retains data in-process that influences future requests.

## Why it matters

Whether a service is stateless or stateful determines how it can be scaled, deployed, and recovered. Stateless services are trivially horizontally scalable and replaceable; stateful services require careful coordination to ensure data is consistent and durable across restarts and node failures.

## How it works

A **stateless** service handles each request using only the data in the request itself and externally stored state (databases, caches). Any replica can serve any request. This makes [load balancing](Load%20Balancing.md), [horizontal scaling](Horizontal%20and%20Vertical%20Scaling.md), rolling deployments, and auto-scaling straightforward — add or remove instances freely.

A **stateful** service maintains in-process state (session data, connection pools, in-memory caches, stream offsets, open file handles) that must be preserved or migrated when the process moves. Stateful services require:
- **[Replication](../Databases/Replication.md)** to survive node failures
- **Sticky routing** via [consistent hashing](../Algorithms/Consistent%20Hashing.md) or session affinity to route related requests to the same instance
- **Leader election** or coordination on failover

Many services are **partially stateful**: an in-process cache makes them faster but means a restart serves cold traffic until the cache warms. Easy to scale out, but warm-up latency must be accounted for.

## Key tradeoffs

- Pushing all state to an external store makes a service stateless but adds latency, a network hop, and a dependency on the store's availability
- Stateful services achieve lower latency by keeping hot data in memory but pay high operational overhead for failure handling, scaling, and zero-downtime upgrades
- The "stateless" label is often aspirational — even services with external state have partial statefulness (connection pools, local caches, open sockets) that affects behavior during restarts

## Related concepts

- [Horizontal and Vertical Scaling](Horizontal%20and%20Vertical%20Scaling.md) — stateless services scale horizontally without coordination; statefulness is the primary barrier to horizontal scaling
- [Load Balancing](Load%20Balancing.md) — stateless services allow any load balancing algorithm; stateful services may require session affinity or consistent-hash routing
- [Service Discovery](Service%20Discovery.md) — stateful services may need routing to specific instances, not just any healthy instance; service discovery must support instance-level addressing
- [Replication](../Databases/Replication.md) — stateful services achieve fault tolerance through replication; without it, a node failure means data loss
- [Consistent Hashing](../Algorithms/Consistent%20Hashing.md) — the standard way to route stateful requests to the correct node while minimizing redistribution when the cluster changes
