import os

import hypernetx as hnx
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import cm
from matplotlib.text import Annotation
from plotting_utils import save_pgf_fig, set_rcParams

from hyperbard.statics import PAPERGRAPHICS_PATH


def draw_toy(G, pos, ax, path):
    nx.draw_networkx_edges(G, pos=pos)
    for n, position in pos.items():
        if n.isnumeric():
            label = int(n) + 1
        else:
            label = n
        txt = ax.annotate(label, position, ha="center", va="center")
        txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])
    plt.axis("off")
    plt.tight_layout()
    save_pgf_fig(path)


if __name__ == "__main__":
    os.makedirs(PAPERGRAPHICS_PATH, exist_ok=True)
    set_rcParams(fontsize=56)

    # Toy data scenario
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    characters = [A, B, C, D, E]
    interactions = [[A], [A, B], [A, B, C], [B, C], [C], [C, D], [A, B, C, D, E]]

    # Create and draw hypergraph
    H = hnx.Hypergraph(interactions)
    edge_labels = {i.uid: int(i.uid) + 1 for i in H.edges()}
    edge_colors = [
        cm.viridis_r(x / H.number_of_edges()) for x in range(H.number_of_edges())
    ]

    fig, ax = plt.subplots(1, 1, figsize=(7, 7))
    hnx.draw(
        H,
        edge_labels=edge_labels,
        layout_kwargs=dict(seed=1234),
        edges_kwargs=dict(edgecolors=edge_colors, lw=3, dr=0.0),
        label_alpha=0,
        node_radius=2.75,
    )
    for child in ax.get_children():
        if isinstance(child, Annotation):
            child.set_path_effects(
                [PathEffects.withStroke(linewidth=5, foreground="w")]
            )
    plt.tight_layout()
    save_pgf_fig(f"{PAPERGRAPHICS_PATH}/toy_drama_hg.pdf")

    # Star expansion
    bG = H.bipartite()
    fig, ax = plt.subplots(1, 1, figsize=(7, 7))
    pos = {
        **{
            k: (0, 1 - (idx / (len(characters) - 1)))
            for idx, k in enumerate(
                [n for n, b in bG.nodes(data="bipartite") if b == 0]
            )
        },
        **{
            k: (1, 1 - (idx / (len(interactions) - 1)))
            for idx, k in enumerate(
                [n for n, b in bG.nodes(data="bipartite") if b == 1]
            )
        },
    }
    draw_toy(bG, pos=pos, ax=ax, path=f"{PAPERGRAPHICS_PATH}/toy_drama_se.pdf")

    # Clique expansion
    G = nx.bipartite.projection.projected_graph(bG, characters)
    fig, ax = plt.subplots(1, 1, figsize=(7, 7))
    pos = nx.circular_layout(G)
    draw_toy(G, pos=pos, ax=ax, path=f"{PAPERGRAPHICS_PATH}/toy_drama_ce.pdf")
