# Horizontal and Vertical Scaling

Horizontal scaling adds more nodes to handle load; vertical scaling upgrades the capacity of existing nodes.

## Why it matters

Every service eventually exceeds the capacity of a single machine. Choosing how to scale affects cost, complexity, fault tolerance, and the fundamental architecture of the system.

## How it works

**Vertical scaling** (scaling up) increases CPU, RAM, or storage on an existing node. It requires no application changes and has no distribution overhead, but is bounded by the largest available hardware and leaves a single point of failure. Useful for stateful services that are hard to distribute.

**Horizontal scaling** (scaling out) adds identical nodes behind a [load balancer](Load%20Balancing.md). It is theoretically unbounded and improves fault tolerance — no single node failure takes down the service — but requires the application to be stateless or to explicitly manage distributed state. [Stateless services](Stateless%20and%20Stateful%20Services.md) scale out trivially; stateful services require [replication](../Databases/Replication.md), [sharding](../Databases/Sharding.md), or [consistent hashing](../Algorithms/Consistent%20Hashing.md) to distribute their state.

Most systems use both: vertically scale to a comfortable size, then horizontally scale beyond that ceiling.

## Key tradeoffs

- Vertical scaling has a hard ceiling set by available hardware and creates a single point of failure; horizontal scaling has no hard ceiling but requires stateless design or distributed state management
- Horizontal scaling introduces coordination overhead: [load balancing](Load%20Balancing.md), distributed consensus, data sharding; vertical scaling has none of this
- Cost curves differ: vertical scaling is often cheaper and simpler at low scale; horizontal scaling becomes more cost-efficient at high scale using commodity hardware

## Related concepts

- [Load Balancing](Load%20Balancing.md) — horizontal scaling requires a load balancer to distribute traffic across the pool of instances
- [Stateless and Stateful Services](Stateless%20and%20Stateful%20Services.md) — stateless services scale horizontally without coordination; stateful services require additional mechanisms
- [Replication](../Databases/Replication.md) — databases scale reads horizontally via read replicas; writes scale via sharding
- [Sharding](../Databases/Sharding.md) — horizontal scaling for databases requires sharding to distribute both data and write load
- [Consistent Hashing](../Algorithms/Consistent%20Hashing.md) — enables horizontal scaling of caches and leaderless databases by minimizing data movement when nodes are added or removed
