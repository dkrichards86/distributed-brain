#!/usr/bin/env python3
"""Generate a knowledge graph PNG from markdown backlinks."""

import math
import re
from pathlib import Path
from urllib.parse import unquote

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

VAULT = Path(__file__).parent
SKIP = {"README.md", "CLAUDE.md"}
OUTPUT = VAULT / "graph.png"

CATEGORY_COLORS = {
    "Algorithms": "#4e9af1",
    "Architecture": "#f1a24e",
    "Databases": "#4ef18a",
    "Distributed Systems": "#f14e4e",
    "Engineering": "#a24ef1",
    "Fault Tolerance": "#f1e44e",
    "Messaging": "#4ef1e4",
    "Observability": "#f14ea2",
    "Performance": "#a2f14e",
    "Serialization & RPC": "#f17c4e",
}
DEFAULT_COLOR = "#bbbbbb"


def note_label(path: Path) -> str:
    return path.stem


def note_category(path: Path) -> str:
    rel = path.relative_to(VAULT)
    parts = rel.parts
    return parts[0] if len(parts) > 1 else ""


def collect_notes() -> dict[str, Path]:
    notes = {}
    for p in VAULT.rglob("*.md"):
        if p.name in SKIP:
            continue
        notes[note_label(p)] = p
    return notes


def parse_links(md_path: Path, all_notes: dict[str, Path]) -> list[str]:
    text = md_path.read_text(encoding="utf-8")
    targets = []
    for raw in re.findall(r"\[.*?\]\(([^)]+\.md[^)]*)\)", text):
        raw = raw.split("#")[0]
        decoded = unquote(raw)
        target_path = (md_path.parent / decoded).resolve()
        label = target_path.stem
        if label in all_notes and label != note_label(md_path):
            targets.append(label)
    return targets


def build_graph(notes: dict[str, Path]) -> nx.DiGraph:
    G = nx.DiGraph()
    for label, path in notes.items():
        G.add_node(label, category=note_category(path))
    for label, path in notes.items():
        for target in parse_links(path, notes):
            G.add_edge(label, target)
    return G


def cluster_layout(G: nx.Graph) -> dict:
    """Two-level force layout: spread community centers, spring within each cluster."""
    communities = list(greedy_modularity_communities(G))
    n = len(communities)

    # Place community centers on a circle
    centers = {
        i: (math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n))
        for i in range(n)
    }

    pos = {}
    for i, community in enumerate(communities):
        subgraph = G.subgraph(community)
        cx, cy = centers[i]
        # Tighter spring layout within each cluster
        spread = max(0.08, 0.35 / math.sqrt(len(community)))
        sub_pos = nx.spring_layout(subgraph, k=spread, iterations=80, seed=42)
        for node, (x, y) in sub_pos.items():
            # Scale sub-positions and offset to community center
            pos[node] = (cx + x * 0.55, cy + y * 0.55)

    return pos


def draw(G: nx.DiGraph, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(22, 18))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    undirected = G.to_undirected()
    pos = cluster_layout(undirected)

    node_colors = [
        CATEGORY_COLORS.get(G.nodes[n].get("category", ""), DEFAULT_COLOR)
        for n in G.nodes
    ]
    degrees = dict(undirected.degree())
    node_sizes = [max(180, degrees[n] * 110) for n in G.nodes]

    # Draw inter-cluster edges dimmer than intra-cluster edges
    communities = list(greedy_modularity_communities(undirected))
    node_to_community = {n: i for i, c in enumerate(communities) for n in c}

    intra = [(u, v) for u, v in G.edges() if node_to_community.get(u) == node_to_community.get(v)]
    inter = [(u, v) for u, v in G.edges() if node_to_community.get(u) != node_to_community.get(v)]

    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=inter,
                           edge_color="#33334d", width=0.5, alpha=0.4, arrows=False)
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=intra,
                           edge_color="#6666aa", width=0.8, alpha=0.7, arrows=False)
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_colors, node_size=node_sizes, alpha=0.93)
    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_size=6.5, font_color="#eeeeee", font_family="monospace")

    handles = [
        mpatches.Patch(color=color, label=cat)
        for cat, color in sorted(CATEGORY_COLORS.items())
        if any(G.nodes[n].get("category") == cat for n in G.nodes)
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=8,
              facecolor="#2a2a4e", edgecolor="#555577", labelcolor="white", framealpha=0.85)

    ax.axis("off")
    plt.tight_layout(pad=0.5)
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved {out} ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")


if __name__ == "__main__":
    notes = collect_notes()
    G = build_graph(notes)
    draw(G, OUTPUT)
