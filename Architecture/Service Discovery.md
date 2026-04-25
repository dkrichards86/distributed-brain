# Service Discovery

The mechanism by which services in a distributed system dynamically locate the network endpoints of their dependencies, replacing hardcoded addresses with real-time registry lookups.

## Why it matters

In static deployments you can hardcode IP addresses in config. In dynamic environments — containers, autoscaling groups, rolling deployments, multi-region failover — instances start and stop continuously and IPs change with every restart. Service discovery gives every service a stable logical name (`orders-service`, `payments-api`) and keeps the set of healthy endpoints behind that name up to date in real time. Without it, deployments require coordinated config updates across all services, and instance failures require manual intervention.

## How it works

### Registration

Instances register their address when they start:
- **Self-registration** — the service calls the registry API on startup (e.g., Consul's `/v1/agent/service/register`) and deregisters on shutdown. Simple but requires the service to carry registry-client code.
- **Third-party registration** — a platform component (Kubernetes controller, ECS agent) watches the runtime and registers/deregisters instances. Services are unaware of the registry.

### Health checking

The registry removes instances from the pool when they fail. Three health check models:
- **HTTP/TCP probe** — the registry sends synthetic requests to a `/health` endpoint; removes instances that fail N consecutive checks
- **TTL heartbeat** — the service must call the registry within a time window; missing the window marks the instance unhealthy (inverts the probe direction)
- **Sidecar/agent** — a local [sidecar](Sidecar.md) performs the health check and reports to the registry; isolates health check traffic from application traffic

### Discovery patterns

**Client-side discovery**: The client queries the registry directly, gets a list of healthy endpoints, and applies its own [load balancing](Load%20Balancing.md) algorithm.
- Examples: Netflix Eureka + Ribbon, Consul + client library
- Pro: one fewer network hop per request, client controls the load balancing algorithm
- Con: every language needs the registry client library; clients must handle cache staleness

**Server-side discovery**: The client sends requests to a proxy or [load balancer](Load%20Balancing.md) that queries the registry internally and forwards to a live instance.
- Examples: AWS ALB + ECS, Envoy sidecar, Kubernetes Service + kube-proxy
- Pro: client is simple; discovery and load balancing are centralized
- Con: proxy is in the critical path; adds a network hop; proxy availability matters

**DNS-based discovery**: The registry publishes healthy endpoints as DNS A records. The client resolves the service name via DNS and connects to the returned IP.
- Examples: Kubernetes Services, Consul DNS, AWS Route 53 + health checks
- Pro: universally supported; no special client required
- Con: DNS TTLs create lag between health check failure and removal from rotation; no rich metadata

### Common registries

- **Consul** — health checks, K/V store, multi-datacenter support, DNS and HTTP API
- **etcd** — used by Kubernetes; strong consistency via Raft; lower-level than Consul
- **ZooKeeper** — original distributed registry; more operational complexity
- **Kubernetes Services** — built-in; kube-proxy programs iptables rules for cluster-internal discovery
- **Eureka** — Netflix open-source; AP (favors availability over consistency)

[Gossip protocols](../Distributed%20Systems/Gossip%20Protocols.md) are used by registries like Consul and Serf to propagate membership changes across nodes without a centralized coordinator, enabling the registry itself to be distributed and fault-tolerant.

## Key tradeoffs

- **Registry availability** — if the registry is down, clients that haven't cached endpoint lists can't establish new connections; registries themselves must be highly available and typically run as a Raft cluster (Consul, etcd)
- **Cache staleness vs. registry load** — clients that cache endpoint lists reduce registry load but may send requests to recently-failed instances; the staleness window must be shorter than the [failure detection](../Fault%20Tolerance/Failure%20Detection.md) latency
- **Client-side vs. server-side complexity** — client-side discovery is faster but multiplies the registry-client implementation across every service and language; server-side discovery centralizes complexity in the proxy but makes the proxy a critical path component
- **DNS simplicity vs. feature richness** — DNS-based discovery works everywhere but doesn't support health-weight metadata, multiple ports per instance, or real-time removal; rich registries support all of these at the cost of integration complexity

## Related concepts

- [Service Mesh](Service%20Mesh.md) — the control plane of a service mesh is a service discovery system; it translates service names to endpoint lists and pushes them to sidecar proxies via the xDS API
- [Load Balancing](Load%20Balancing.md) — service discovery provides the pool of endpoints; load balancing selects which one to use for each request
- [Sidecar](Sidecar.md) — in service mesh deployments, the sidecar proxy receives endpoint lists from the control plane and performs client-side discovery transparently
- [Gossip Protocols](../Distributed%20Systems/Gossip%20Protocols.md) — Consul uses gossip (via Serf) to propagate node join/leave events across the registry cluster
- [Failure Detection](../Fault%20Tolerance/Failure%20Detection.md) — registries use health checks to detect failed instances; the same detection latency tradeoffs apply
- [gRPC](../Serialization%20%26%20RPC/gRPC.md) — gRPC has a pluggable name resolver interface that integrates with service registries; it supports xDS natively for Envoy-based service discovery
- [Health Checks](../Observability/Health%20Checks.md) — service registries perform health checks (HTTP probes, TTL heartbeats) to determine which instances to include in the endpoint pool
