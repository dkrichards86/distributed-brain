# Chaos Engineering

The practice of deliberately injecting failures into a production (or production-like) system to discover weaknesses before they cause unplanned outages.

## Why it matters

Every distributed system has failure modes that only manifest at scale or in combinations that are hard to predict from code review or unit tests. Circuit breakers that never open, failover logic that's never been exercised, timeouts that are too generous — these are invisible until a real incident. Chaos engineering surfaces these weaknesses in controlled experiments so teams can fix them proactively rather than discover them at 3am under customer pressure.

## How it works

### The scientific method applied to systems

Chaos engineering is framed as an experiment:

1. **Hypothesize** — define a steady-state metric (requests per second, error rate, latency p99) and hypothesize the system will maintain it under a given failure condition
2. **Introduce failure** — inject the failure into a small percentage of traffic or infrastructure
3. **Observe** — measure whether the steady-state metric holds; if it doesn't, the system has a weakness
4. **Fix and repeat** — address the weakness, then expand the blast radius of the experiment

### Common failure types

- **Node/instance termination** — kill a random server; does auto-scaling and failover work?
- **Network failures** — introduce latency, packet loss, or partition between specific services; does the [circuit breaker](Circuit%20Breaker.md) open?
- **Resource exhaustion** — fill disk, saturate CPU, exhaust a connection pool; does the system degrade gracefully?
- **Dependency failures** — take down a downstream service or database replica; does the system fall back or fail open/closed correctly?
- **Clock skew** — introduce time drift; does anything depend on clock synchronization in a brittle way?

### Tools

- **Chaos Monkey** (Netflix) — randomly terminates instances in production; the original chaos engineering tool
- **Chaos Toolkit** — open-source framework for defining and running chaos experiments as code
- **AWS Fault Injection Simulator (FIS)** — managed chaos experiments against AWS resources
- **Gremlin** — commercial platform for fine-grained failure injection with rollback support
- **Litmus** (CNCF) — Kubernetes-native chaos engineering

### Game days

Structured exercises where a team simulates a major failure scenario (region outage, database corruption) and works through the response in real time. Combines chaos injection with incident response practice.

## Key tradeoffs

- **Production vs. staging** — staging environments don't reflect production traffic patterns or scale; chaos in staging often misses failure modes; running in production is more valuable but riskier; start with staging, move to production with minimal blast radius
- **Blast radius control** — chaos experiments must be bounded; kill one instance, not the entire fleet; inject failures for one minute, not one hour; always have a kill switch
- **Organizational buy-in** — chaos engineering requires teams to accept deliberate degradation; without leadership support and SRE culture, experiments get blocked before they find anything valuable
- **Steady state definition** — experiments are only meaningful if you define and measure the right metrics; a test that doesn't fail doesn't prove the system is resilient — it might just mean the metric is wrong

## Related concepts

- [Circuit Breaker](Circuit%20Breaker.md) — chaos experiments validate that the breaker opens correctly under failure conditions
- [Bulkhead](Bulkhead.md) — chaos experiments verify that bulkheads contain failures and don't let one path exhaust shared resources
- [Failure Detection](Failure%20Detection.md) — chaos experiments test whether failure detection fires correctly and within expected latency
- [SLOs and Error Budgets](../Observability/SLOs%20and%20Error%20Budgets.md) — chaos experiments consume error budget; the error budget framing provides a principled way to decide how much chaos to run in production
