# Blue-Green and Canary Deployments

Deployment strategies that release new versions with controlled traffic shifting, limiting the blast radius of regressions.

## Why it matters

Deploying a new version to all instances simultaneously risks taking down the entire service if the new version has a bug. Controlled deployment strategies expose the new version to real traffic incrementally, enabling early detection of regressions while keeping most traffic on the stable version.

## How it works

**Blue-green**: two identical production environments (blue = current, green = new) are maintained. The new version is deployed to green and validated (load tests, smoke tests, [health checks](../Observability/Health%20Checks.md)). A load balancer or DNS switch then instantly flips all traffic from blue to green. Rollback is an instant flip back — as long as blue is still running.

**Canary**: the new version is deployed to a small subset of instances (the "canary") and receives a small percentage of real traffic (1–5%). Metrics are monitored for regressions in error rate, latency, and business KPIs. Traffic is gradually shifted to the new version as confidence grows. Rollback removes the canary instances from the [load balancer](Load%20Balancing.md) pool.

[Service meshes](Service%20Mesh.md) enable fine-grained canary traffic splitting at the request level (weighted routing by percentage or by header) rather than at the instance level.

## Key tradeoffs

- Blue-green requires maintaining two full production environments simultaneously during the switchover window — roughly double the infrastructure cost
- Canary rollouts are slower and require automated metric gates to be effective; without them, regressions are caught only if someone is watching dashboards
- Both strategies require the new version to be **backwards compatible** with any shared state (database schema, message format, API contracts) since both versions run simultaneously; migrations must be schema-additive before the old version is removed
- DNS-based blue-green cutover is constrained by TTL propagation time; load-balancer-based switching is effectively instant

## Related concepts

- [Load Balancing](Load%20Balancing.md) — traffic splitting between blue/green or stable/canary is implemented at the load balancer; weighted round-robin is the standard mechanism
- [Health Checks](../Observability/Health%20Checks.md) — new instances must pass health checks before receiving traffic; failed health checks gate promotion and trigger rollback
- [Service Mesh](Service%20Mesh.md) — service meshes implement header-based and percentage-based traffic splitting at the proxy level, enabling canary deployments without changes to the load balancer
