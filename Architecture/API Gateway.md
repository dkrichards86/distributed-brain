# API Gateway

A single entry point that sits in front of a collection of backend services, routing client requests and applying cross-cutting concerns uniformly.

## Why it matters

Clients shouldn't need to know the topology of internal services. The gateway decouples external interfaces from internal decomposition, and centralizes authentication, [rate limiting](../Engineering/Rate%20Limiting.md), TLS termination, and observability in one place instead of duplicating them across every service. It also enables API versioning and request/response transformation without changing backend services.

## How it works

The gateway receives all inbound (north-south) traffic and routes requests to the appropriate upstream service based on path, headers, or method. It applies policies before forwarding:

- **Authentication / authorization** — validate tokens, API keys, or mTLS certificates before the request reaches a service
- **Rate limiting** — enforce per-client or per-endpoint quotas
- **TLS termination** — decrypt HTTPS at the gateway; backends communicate over plain HTTP or [mTLS](mTLS.md) internally
- **Request transformation** — rewrite paths, add/strip headers, translate protocols (REST ↔ gRPC)
- **API composition** — aggregate responses from multiple services into a single client response

The gateway handles **north-south traffic** (external clients to the cluster). A [service mesh](Service%20Mesh.md) handles **east-west traffic** (service to service). The two are complementary, not competing: the gateway is the front door; the mesh manages the interior network.

Common implementations: AWS API Gateway, Kong, Nginx, Envoy, Apigee, Traefik.

## Key tradeoffs

- Adds a network hop and a potential single point of failure — must be deployed with high availability and treated as a critical path component
- Can become a bottleneck and a "god object" if business logic leaks into the gateway layer; the gateway should route and apply infrastructure concerns, not implement domain logic
- Tight coupling between gateway routing config and internal service contracts means service restructuring requires coordinated gateway updates

## Related concepts

- [Load Balancing](Load%20Balancing.md) — the gateway uses load balancing to distribute traffic across backend instances; L7 routing enables path-based and header-based balancing
- [Service Mesh](Service%20Mesh.md) — the mesh manages east-west (service-to-service) traffic; the gateway manages north-south (client-to-cluster) traffic; they complement each other
- [Service Discovery](Service%20Discovery.md) — the gateway resolves backend service names to live endpoints via the service registry
- [Rate Limiting](../Engineering/Rate%20Limiting.md) — rate limiting is one of the primary responsibilities of the gateway; per-client quotas are enforced at the entry point before requests reach backends
- [mTLS](mTLS.md) — the gateway may terminate external TLS and re-establish mTLS connections to backends, or enforce mTLS at the entry point for service-to-gateway authentication
- [Horizontal and Vertical Scaling](Horizontal%20and%20Vertical%20Scaling.md) — the gateway must scale horizontally to handle traffic growth; it is typically stateless to allow scaling without coordination
