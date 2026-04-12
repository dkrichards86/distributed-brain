# Sidecar

A deployment pattern where a helper process runs alongside the primary application container, sharing its network namespace and lifecycle, to provide infrastructure concerns without modifying application code.

## Why it matters

Cross-cutting infrastructure concerns — TLS termination, metrics collection, distributed tracing, retries, circuit breaking — can be implemented in application code, but that means re-implementing them in every language and service. The sidecar pattern moves these concerns to a separate process that runs beside the application, giving you infrastructure capabilities regardless of what language the application is written in or whether its code can be changed.

## How it works

In a containerized environment (Kubernetes), a sidecar is an additional container in the same Pod as the application container. Containers in a Pod share:

- **Network namespace** — same IP address and localhost; the sidecar can intercept traffic by listening on a port or via iptables rules that redirect traffic through it
- **Lifecycle** — start and stop together
- **Mounted volumes** — shared filesystem for log files, configuration, or Unix sockets

### Traffic interception

The most powerful use of the sidecar is as a **transparent proxy**. iptables rules are configured (by the init container or the kubelet) to redirect all inbound and outbound traffic through the sidecar. The application is unaware that its traffic is being intercepted.

The sidecar can then:
- Enforce mutual TLS (mTLS) between services
- Apply retry and timeout policies
- Collect request metrics and traces
- Enforce authorization policies
- Implement circuit breaking

Envoy proxy is the dominant sidecar implementation for this use case.

### Non-proxy sidecars

Not all sidecars intercept traffic. Other patterns:

- **Log forwarder** — tails log files from a shared volume and ships them to a log aggregation system (Fluentd, Filebeat alongside an application)
- **Config watcher** — polls a configuration service and writes updated config to a shared volume; the application reloads from the file
- **Metrics agent** — scrapes application metrics from a local endpoint and forwards to a metrics backend
- **Secret injector** — fetches secrets from a vault and writes them to a shared in-memory volume; secrets never touch the filesystem

## Key tradeoffs

- **Resource overhead** — every pod runs an extra process consuming memory and CPU; at thousands of pods, this adds up; Envoy typically adds 50–100ms of CPU-milliseconds per request and ~100MB of memory
- **Operational complexity** — sidecar lifecycle, configuration, and upgrades must be managed; this is what a [service mesh](Service%20Mesh.md) control plane solves
- **Latency** — traffic intercepted through a proxy adds a network hop (loopback, but still); typically sub-millisecond but measurable in latency-sensitive paths
- **Not for all workloads** — sidecars require containerized deployments; batch jobs, VMs, or serverless functions need different approaches (eBPF-based proxies, SDK-based instrumentation)

## Related concepts

- [Service Mesh](Service%20Mesh.md) — a service mesh is the fleet-wide deployment and management of sidecars; the sidecar is the data plane, the mesh control plane configures it
- [Circuit Breaker](../Fault%20Tolerance/Circuit%20Breaker.md) — circuit breakers are commonly implemented in the sidecar proxy, removing the concern from application code
