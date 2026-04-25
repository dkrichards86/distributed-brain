# Service Mesh

An infrastructure layer that manages service-to-service communication in a microservices architecture by deploying a network of sidecar proxies and a control plane to configure them.

## Why it matters

As microservice counts grow, cross-cutting concerns — mutual TLS, retries, circuit breaking, load balancing, distributed tracing — become difficult to manage consistently across every service. Without a service mesh, each team implements these independently, in their language, at different levels of correctness. A service mesh moves these concerns below the application layer so they apply uniformly without changing application code.

## How it works

### Data plane

The data plane is the set of [sidecar](Sidecar.md) proxies deployed alongside every service instance. In Istio and Linkerd, this is Envoy (or a Linkerd2-proxy). These proxies intercept all inbound and outbound traffic via iptables rules, transparent to the application.

The data plane enforces:
- **[mTLS](mTLS.md)** — every connection between services is encrypted and both sides present a certificate; no service can impersonate another
- **[Load balancing](Load%20Balancing.md)** — sophisticated algorithms (least-connections, locality-aware) beyond what DNS-based load balancing can do
- **[Retries and timeouts](../Fault%20Tolerance/Retries%20and%20Timeouts.md)** — configured per-route, applied consistently regardless of client implementation
- **[Circuit breaking](../Fault%20Tolerance/Circuit%20Breaker.md)** — opens when a destination shows errors above a threshold
- **Observability** — [request metrics](../Observability/Metrics%20and%20Percentiles.md) and [traces](../Observability/Distributed%20Tracing.md) generated for every call without application instrumentation

### Control plane

The control plane configures the proxies. Applications declare desired behavior via Kubernetes custom resources (VirtualService, DestinationRule, PeerAuthentication in Istio). The control plane translates these into xDS API updates pushed to each proxy.

Key responsibilities:
- Certificate issuance and rotation for mTLS
- Service discovery (translating service names to endpoint lists)
- Policy distribution (which retries, which circuit breaker thresholds)
- Traffic splitting for canary deployments and A/B tests

### Common implementations

- **Istio** — most feature-rich; Envoy data plane; complex to operate; supports advanced traffic management (traffic mirroring, fault injection, weighted routing)
- **Linkerd** — simpler, lighter, Rust-based proxy with lower overhead; focuses on core reliability features
- **Consul Connect** — integrated with Consul service discovery; good for multi-runtime environments (VMs + containers)
- **AWS App Mesh** — managed control plane for ECS/EKS workloads

## Key tradeoffs

- **Uniform capability vs. operational complexity** — a service mesh gives you consistent mTLS, observability, and reliability for every service, but adds a control plane to operate, debug, and upgrade; misconfigurations can cause cluster-wide outages
- **Latency overhead** — two additional proxy hops per service call (client-side and server-side); Envoy adds ~0.5–2ms per hop depending on configuration; significant for high-RPS, low-latency services
- **Resource cost** — sidecar proxies consume CPU and memory at every pod; a 1,000-pod cluster running Envoy adds meaningful infrastructure cost
- **Adoption friction** — retrofitting a mesh onto an existing cluster requires injecting sidecars into every deployment; testing and rollout is non-trivial

## Related concepts

- [Sidecar](Sidecar.md) — the service mesh data plane is a fleet of sidecars; the mesh adds the control plane that configures them centrally
- [Circuit Breaker](../Fault%20Tolerance/Circuit%20Breaker.md) — circuit breakers are a core feature of service mesh proxies; the mesh applies them consistently without application code changes
- [Bulkhead](../Fault%20Tolerance/Bulkhead.md) — service meshes enforce connection limits and concurrency caps at the proxy level, implementing bulkhead semantics without application changes
- [Failure Detection](../Fault%20Tolerance/Failure%20Detection.md) — the service mesh proxy detects failing upstreams and opens circuit breakers; it's failure detection at the call level
- [Distributed Tracing](../Observability/Distributed%20Tracing.md) — service meshes generate trace spans for every service-to-service call; tracing headers must still be propagated by the application
- [Service Discovery](Service%20Discovery.md) — the service mesh control plane is a service discovery system; it resolves service names to endpoint lists and pushes them to sidecar proxies via xDS
- [API Gateway](API%20Gateway.md) — the gateway handles north-south traffic (clients to cluster); the mesh handles east-west traffic (service to service); they are complementary
