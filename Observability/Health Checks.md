# Health Checks

Periodic probes that determine whether a service instance is alive and capable of serving traffic.

## Why it matters

In a distributed system, instances can crash, deadlock, run out of memory, or lose connectivity to their dependencies without necessarily exiting cleanly. Health checks give the infrastructure — load balancers, orchestrators, service registries — a signal to route around or restart degraded instances automatically, without human intervention.

## How it works

Two probe types are standard:

**Liveness** — is the process alive at all? A failing liveness check indicates the process is deadlocked, OOM-killed, or otherwise unrecoverable. The orchestrator (Kubernetes, ECS) restarts the instance. The liveness endpoint must be lightweight and must not depend on downstream services — a slow database should not make a healthy process appear dead.

**Readiness** — is the instance ready to serve traffic? A failing readiness check indicates the instance is still starting up, warming caches, or temporarily unable to reach a dependency. The load balancer removes the instance from rotation without restarting it. Readiness checks can depend on downstream services; liveness checks should not.

Probes are typically HTTP endpoints (`/health/live`, `/health/ready`), TCP connections, or exec commands run by the orchestrator on a configurable interval. Kubernetes configuration example: check every 10 seconds, fail after 3 consecutive failures, wait 30 seconds on startup before probing.

Service registries ([Consul](../Architecture/Service%20Discovery.md), etcd) use similar health checks to maintain the pool of healthy endpoints — instances that fail checks are removed from the registry.

## Key tradeoffs

- Liveness probes that are too aggressive restart healthy instances under temporary load (GC pause, slow startup); failure thresholds and initial delay must be tuned per service
- Readiness checks that depend on downstream services cause cascading removal: if a shared database slows, all services depending on it may fail readiness simultaneously, taking down the entire fleet
- Health endpoints must be lightweight and self-contained — a health check that itself makes database calls can cascade failures

## Related concepts

- [Circuit Breaker](../Fault Tolerance/Circuit%20Breaker.md) — circuit breakers detect failure at the call level; health checks detect it at the instance level; both feed into traffic routing decisions
- [Failure Detection](../Fault%20Tolerance/Failure%20Detection.md) — health checks are a form of failure detection; the same accuracy/latency tradeoff applies: shorter intervals detect failures faster but increase false positives
- [Load Balancing](../Architecture/Load%20Balancing.md) — load balancers use active health checks to maintain the pool of healthy backends; instances failing readiness are removed from rotation
- [Service Discovery](../Architecture/Service%20Discovery.md) — service registries perform health checks to determine which instances to include in the endpoint pool
- [Blue-Green and Canary Deployments](../Architecture/Blue-Green%20and%20Canary%20Deployments.md) — health checks gate traffic promotion in both strategies; new instances must pass health checks before receiving production traffic
