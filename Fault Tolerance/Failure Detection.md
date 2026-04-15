# Failure Detection

The mechanism by which distributed systems determine that a node is unavailable, so that the system can respond — triggering re-election, rerouting traffic, or removing the node from rotation.

## Why it matters

A node that is slow looks identical to a node that has crashed, from the outside. Without a principled failure detector, a system either waits too long (treating a crashed node as slow, blocking progress) or declares failures too aggressively (evicting nodes that are just lagging, causing unnecessary disruption). Getting this right is prerequisite to [leader election](../Distributed%20Systems/Leader%20Election.md), [consensus](../Distributed%20Systems/Consensus%20Algorithms.md), and failover.

## How it works

### Heartbeats

The simplest approach. Each node periodically sends a "I'm alive" signal to a monitor (or peers). If no heartbeat is received within a timeout window, the node is declared dead.

**Fixed timeout problems:**
- Too short: false positives under GC pauses, network hiccups, or CPU saturation — healthy nodes get evicted
- Too long: slow failure detection means extended unavailability

Heartbeat intervals in production systems are typically 1–5 seconds with timeouts of 3–10x the interval.

### Phi Accrual Failure Detector

Rather than a binary alive/dead verdict, the Phi Accrual detector outputs a continuous **suspicion level** φ (phi). The caller decides the threshold at which to act.

**How it works:**
1. Maintain a sliding window of recent heartbeat inter-arrival times
2. Model the inter-arrival distribution (typically normal or exponential)
3. Given the time since the last heartbeat, compute φ = -log₁₀(probability that the next heartbeat arrives this late or later under normal conditions)
4. φ rises continuously as time passes without a heartbeat; at φ = 8, the probability of a false detection is ~1 in 10⁸

This adapts to network conditions automatically — a cluster with high-variance heartbeat timing sets a wider distribution, so φ rises more slowly, reducing false positives. Used by Cassandra and Akka.

### SWIM (Scalable Weakly-consistent Infection-style Membership)

A gossip-based failure detection protocol designed for large clusters where a central monitor is a bottleneck.

- Each node periodically picks a random peer and sends it a **ping**
- If no ack arrives within a deadline, the node picks `k` random other nodes and asks them to probe the suspect (**indirect ping**) — this distinguishes "crashed" from "network partition between me and that node"
- If no ack arrives via any path, the node is marked **suspect** and the suspicion is gossiped to the cluster
- If the suspect doesn't refute its suspicion within a timeout, it's confirmed dead and the confirmation is gossiped

SWIM's key insight: detection work is spread across all nodes (no central monitor bottleneck) and the gossip dissemination is piggy-backed on the same messages.

## Key tradeoffs

- **False positives vs. detection latency** — shorter timeouts detect failures faster but increase false evictions; longer timeouts reduce false positives but extend the window of unavailability
- **Completeness vs. accuracy** — a detector is complete if it eventually detects all failures, accurate if it never suspects a live node; you can't have both in an asynchronous system (FLP impossibility), so real detectors trade one for the other
- **Central monitor vs. gossip-based** — centralized monitors are simple but add load and become bottlenecks at scale; gossip-based detection (SWIM) scales better but converges more slowly

## Related concepts

- [Leader Election](../Distributed%20Systems/Leader%20Election.md) — election is triggered by failure detection; the sensitivity of the detector directly determines election frequency and failover latency
- [Consensus Algorithms](../Distributed%20Systems/Consensus%20Algorithms.md) — Raft's election timeout is a simple heartbeat-based failure detector; when a follower stops hearing from the leader, it starts an election
- [Gossip Protocols](../Distributed%20Systems/Gossip%20Protocols.md) — SWIM uses gossip for disseminating failure suspicions across the cluster
- [Circuit Breaker](Circuit%20Breaker.md) — failure detection at the service-call level; the breaker opens when a downstream looks like it's failing, rather than waiting for node-level detection
- [Service Discovery](../Architecture/Service%20Discovery.md) — service registries use health checks to detect failed instances and remove them from the endpoint pool; the same detection latency tradeoffs apply
