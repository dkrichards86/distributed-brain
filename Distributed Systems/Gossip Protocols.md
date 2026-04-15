# Gossip Protocols

An epidemic-style communication protocol where nodes periodically exchange state with a random subset of peers until information spreads to the entire cluster.

## Why it matters

In a large cluster, broadcasting information to every node via a central coordinator is a bottleneck and single point of failure. Gossip provides decentralized, self-healing information dissemination — no coordinator needed, and the protocol degrades gracefully as nodes fail. It's the backbone of cluster membership, failure detection, and state synchronation in many large-scale distributed systems.

## How it works

Each node, on a fixed interval (typically 1–2 seconds), selects one or more random peers and exchanges its current state. The recipient merges the received state with its own and may propagate it further in subsequent rounds.

**Convergence:** gossip spreads information logarithmically — with `N` nodes and fanout `k`, information reaches all nodes in `O(log N / log k)` rounds. This is fast enough in practice (a 1,000-node cluster converges in ~10 gossip rounds) while keeping per-node message volume low.

### Anti-entropy

Nodes periodically synchronize their full state with a random peer to repair divergence. Useful for catching up nodes that missed messages or rejoined after a failure. Slower than pure gossip (full state exchange is expensive) but guarantees convergence even under message loss.

### Rumor-mongering vs. anti-entropy

- **Rumor-mongering** — nodes gossip about new updates ("I just heard X"); stops spreading a rumor after it's been shared with enough nodes. Fast propagation, but can miss nodes.
- **Anti-entropy** — nodes periodically do a full state sync with a peer. Slower but complete. Most systems combine both.

### Applications

- **Cluster membership** — Cassandra and Consul use gossip to propagate node join/leave events. Each node maintains a view of the cluster; gossip keeps that view eventually consistent.
- **Failure detection** — gossip-based failure detectors (like SWIM) spread suspicion and confirmation of node failures across the cluster without a central monitor.
- **State replication** — Redis Cluster uses gossip to propagate slot assignments and node states across all nodes.

## Key tradeoffs

- **Eventual vs. strong consistency** — gossip is eventually consistent; all nodes converge but not simultaneously. Not suitable for operations that require immediate global agreement (use [consensus algorithms](Consensus%20Algorithms.md) for that).
- **Message overhead** — fanout and frequency are tunable; too low and convergence is slow, too high and you flood the network. In large clusters, even O(log N) messages per round can add up.
- **Churn sensitivity** — in clusters with frequent join/leave events, gossip state can lag; systems combine gossip with explicit membership protocols (SWIM, Serf) to handle churn efficiently.

## Related concepts

- [Failure Detection](../Fault%20Tolerance/Failure%20Detection.md) — the SWIM protocol uses gossip to disseminate failure suspicions; gossip is the dissemination layer, phi accrual is the detection layer
- [Consensus Algorithms](Consensus%20Algorithms.md) — gossip handles membership and soft state; consensus handles hard decisions (who is leader, is this transaction committed)
- [Consistent Hashing](../Algorithms/Consistent%20Hashing.md) — gossip propagates ring membership changes in consistent hashing-based systems like Cassandra
- [Service Discovery](../Architecture/Service%20Discovery.md) — Consul uses gossip (via Serf) to propagate node join/leave/failure events across the registry cluster itself
