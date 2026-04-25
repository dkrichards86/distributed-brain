# Load Balancing

Distributing incoming requests across a pool of backend instances to maximize throughput, minimize response time, and avoid overloading any single node.

## Why it matters

A single backend instance has bounded capacity. Load balancing is what turns a pool of instances into a single logical service — it hides the fleet behind one address and routes each request to an instance that can handle it. Without it, traffic is unevenly distributed: some instances are saturated while others are idle, and a single instance failure makes the service appear down.

## How it works

### Algorithms

**Round robin** — requests are distributed to backends in a fixed rotation. Simple, zero-overhead. Falls apart when requests have highly variable cost (a slow request on one backend holds up its "turn" relative to others).

**Weighted round robin** — like round robin but backends are assigned weights proportional to their capacity. Useful when instances have different specs or when gradually shifting traffic (canary deployments).

**Least connections** — each new request goes to the backend with the fewest active connections. Better than round robin for variable-cost workloads; requires the load balancer to track connection counts.

**Least response time** — routes to the backend with the lowest combination of active connections and response latency. More sophisticated, requires real-time latency tracking per backend.

**Random with two choices (P2C)** — pick two backends at random and route to whichever has fewer active requests. Provably near-optimal distribution with O(1) overhead and no shared state between load balancer instances. Used in Envoy and many high-performance load balancers.

**IP hash / consistent hashing** — routes requests from the same client (or for the same key) to the same backend. Provides session affinity. See [Consistent Hashing](../Algorithms/Consistent%20Hashing.md) for the mechanism.

### Layer 4 vs. Layer 7

**Layer 4 (transport)** — routes based on IP and TCP/UDP port. Fast; the load balancer doesn't inspect the payload. Can't make routing decisions based on request content (URL path, headers, gRPC method).

**Layer 7 (application)** — inspects the HTTP/gRPC payload. Can route based on URL path, host header, gRPC service name, or custom headers. Enables path-based routing, header-based canaries, and gRPC-aware load balancing (gRPC streams are long-lived; L4 round robin sends all requests from one stream to one backend).

[Service mesh](Service%20Mesh.md) sidecars operate at Layer 7, which is what enables per-route retry policies and header-based traffic splitting.

### Health checking

The load balancer must know which backends are healthy. Passive health checking infers health from response codes and timeouts on real traffic. Active health checking sends synthetic probes (HTTP GET to a `/health` endpoint) on a timer. Backends that fail checks are removed from the pool; backends that recover are added back.

### Locality-aware routing

In multi-zone or multi-region deployments, routing to the nearest healthy backend reduces latency. Envoy's locality-weighted load balancing sends traffic to the local zone first and only spills over to other zones when local capacity is insufficient.

## Key tradeoffs

- **Statefulness** — stateful algorithms (least connections, P2C) require the load balancer to track per-backend state; this is fine for a single load balancer but requires coordination when multiple load balancer instances share a pool
- **Session affinity cost** — hash-based affinity provides stickiness but can create hot spots if a small number of clients generate disproportionate traffic
- **Health check lag** — backends that fail in between health check intervals still receive traffic; the probe interval vs. detection latency tradeoff mirrors [failure detection](../Fault%20Tolerance/Failure%20Detection.md) generally
- **Long-lived connections** — HTTP/2 and gRPC multiplex many requests over one connection; L4 round robin assigns the connection once, so all requests on that connection go to one backend; L7 load balancing is required to distribute individual requests within a multiplexed connection

## Related concepts

- [Consistent Hashing](../Algorithms/Consistent%20Hashing.md) — the algorithm behind session-affinity and key-based load balancing in distributed databases and caches
- [Service Mesh](Service%20Mesh.md) — the sidecar proxy implements L7 load balancing per-route, including locality awareness and P2C, without application code changes
- [Failure Detection](../Fault%20Tolerance/Failure%20Detection.md) — load balancer health checks are a form of failure detection; the same accuracy/latency tradeoff applies
- [Rate Limiting](../Engineering/Rate%20Limiting.md) — load balancing distributes traffic across backends; rate limiting caps total traffic entering the system; they're complementary
- [Service Discovery](Service%20Discovery.md) — service discovery provides the pool of healthy endpoints that the load balancer selects from; the two concerns are usually co-located in a proxy like Envoy
- [API Gateway](API%20Gateway.md) — the gateway sits in front of the load balancer for north-south traffic, applying auth and routing before load balancing to backend instances
- [Health Checks](../Observability/Health%20Checks.md) — load balancers use active health checks to remove unhealthy backends from the pool; readiness probes gate inclusion in rotation
- [Blue-Green and Canary Deployments](Blue-Green%20and%20Canary%20Deployments.md) — traffic shifting between versions is implemented at the load balancer via weighted routing
- [Horizontal and Vertical Scaling](Horizontal%20and%20Vertical%20Scaling.md) — horizontal scaling adds more instances to the load balancer pool; the load balancer is what makes the pool appear as a single service
