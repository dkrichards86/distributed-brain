# Upstream and Downstream Services

A directional convention describing dependency relationships between services, where "upstream" = the data provider and "downstream" = the data consumer.

## Why it matters

These terms are used constantly in architecture discussions, postmortems, and incident response — and they're counterintuitive enough that people routinely get them backwards. Misaligned terminology during an incident means teams trace failures in the wrong direction. Getting this right (and confirming your team uses the same convention) is table stakes for distributed systems communication.

## How it works

### The river model

Data flows like water. The **source** is upstream. Everything that **receives** data from the source is downstream.

> If Service A calls Service B to get data, **Service B is upstream** to Service A. Service A is downstream from Service B. Data flows from B → A.

Terminology follows **data flow**, not control flow. The service that initiates the request is the consumer — it's downstream. The service that provides the data is the source — it's upstream.

### Why it feels backwards

Your intuition says the calling service is "upstream" because it initiates the request — the call goes "up" to another service and comes back "down." This is control flow thinking.

The convention follows data flow: where does the data originate? That service is upstream. Where does the data end up being consumed? That service is downstream.

### A service can be both

Any service is upstream to some services and downstream from others:

- `Product Service` → `Order Service` → `Frontend`
- `Order Service` is downstream from `Product Service` (consumes product data)
- `Order Service` is upstream to `Frontend` (provides order data)

The terms describe a specific pair-wise relationship, not an absolute position.

### Why it matters operationally

**Failure propagation:** When an upstream service fails, all downstream consumers are affected. If `Auth Service` goes down, every service that depends on it for validation is impacted. Failures and latency cascade **downstream**.

**Blast radius analysis:** Before making a change to a service, identify its downstream consumers — those are the services at risk. Before investigating a problem, identify the upstream dependencies — those are the potential root causes.

**SLA planning:** Your service's [SLA](../Observability/SLOs%20and%20Error%20Budgets.md) is bounded by its upstream dependencies. If `Auth Service` has 99.9% availability and every request requires an auth check, your service can't offer better than 99.9%.

### The team disagreement problem

Not everyone uses these terms the same way. Some teams treat the calling service as upstream. This causes real problems: in incident triage, inverted terminology means teams trace in the wrong direction.

When joining a new team or starting a new project, explicitly confirm the convention: "When we say Service A is upstream to Service B, do we mean A calls B, or B calls A?" Don't assume. Document it.

## Key tradeoffs

- **Terminology clarity vs. convention variance** — the data-flow convention is standard but not universal; the cost of ambiguity during an incident is high enough to warrant explicit confirmation
- **Dependency mapping** — knowing your upstream dependencies is essential for SLA planning; knowing your downstream consumers is essential for assessing change blast radius; both need to be documented

