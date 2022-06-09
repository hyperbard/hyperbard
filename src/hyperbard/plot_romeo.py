from glob import glob

import matplotlib.cm as cm
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import networkx as nx

from hyperbard.graph_io import load_graph
from hyperbard.plotting_utils import save_pgf_fig, set_rcParams
from hyperbard.statics import PAPERGRAPHICS_PATH


def get_formatted_labels(G, selected_labels):
    return {
        n: n if n not in selected_labels else r"\textbf{" + n + "}" for n in G.nodes()
    }


def weighted_multi_to_weighted_simple(G, weight_name):
    new_edges = {(u, v): 0 for u, v in G.edges()}
    for u, v, k, w in G.edges(data=weight_name, keys=True):
        new_edges[(u, v)] += w
    new_nodes = list(G.nodes())
    G_new = nx.Graph()
    G_new.add_nodes_from(new_nodes)
    G_new.add_edges_from(G.edges())
    nx.set_edge_attributes(G_new, new_edges, weight_name)
    return G_new


def position_full_radial_labels(G, labels, pos):
    for n in G.nodes():
        pos_n = pos[n]
        label_n = labels[n]
        if label_n in ["FriarLawrence"]:
            pos_n[-1] += 0.125
        if label_n in ["FriarJohn"]:
            pos_n[-1] += 0.035
        if label_n in ["Gregory"]:
            pos_n[-1] -= 0.075
        ha = "center"
        va = "center"
        txt = ax.annotate(labels[n], pos_n, fontsize=font_size + 6, va=va, ha=ha)
        txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])


if __name__ == "__main__":
    set_rcParams()
    height = 6
    font_size = 16

    selected_labels = ["Juliet", "Romeo", "Capulet", "LadyCapulet", "Nurse"]

    # Radials for the entire play, with all named characters
    G1 = load_graph(
        "romeo-and-juliet",
        "ce-scene-w",
    )

    fig, ax = plt.subplots(1, 1, figsize=(height + 1, height))

    labels = get_formatted_labels(G1, selected_labels)
    pos = nx.circular_layout(G1)

    nx.draw_networkx_edges(
        G1,
        pos=pos,
        ax=ax,
        edge_cmap=cm.Reds,
        edge_vmin=0,
        edge_vmax=1,
        edge_color=[0.5] * G1.number_of_edges(),
        node_size=50,
    )
    position_full_radial_labels(G1, labels, pos)
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_ce-scene-b.pdf",
        axis_off=True,
        tight=True,
    )

    G2 = load_graph("romeo-and-juliet", "ce-scene-w", edge_weights="count")

    fig, ax = plt.subplots(1, 1, figsize=(height + 1, height))

    labels = get_formatted_labels(G2, selected_labels)
    pos = nx.circular_layout(G2)

    sorted_edges = [
        (u, v) for u, v, w in sorted(G2.edges(data="count"), key=lambda tup: tup[-1])
    ]
    sorted_counts = [
        w for u, v, w in sorted(G2.edges(data="count"), key=lambda tup: tup[-1])
    ]

    vmin = min([w for u, v, w in G2.edges(data="count")])
    vmax = max([w for u, v, w in G2.edges(data="count")])

    nx.draw_networkx_edges(
        G2,
        pos=pos,
        ax=ax,
        edge_cmap=cm.Reds,
        edgelist=sorted_edges,
        edge_vmin=vmin,
        edge_vmax=vmax,
        edge_color=sorted_counts,
        width=sorted_counts,
        node_size=50,
    )
    position_full_radial_labels(G2, labels, pos)
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_ce-scene-mb.pdf",
        axis_off=True,
        tight=True,
    )

    G3 = load_graph("romeo-and-juliet", "ce-scene-mw", edge_weights="n_lines")
    G3 = weighted_multi_to_weighted_simple(G3, "n_lines")

    sorted_edges = [
        (u, v) for u, v, w in sorted(G3.edges(data="n_lines"), key=lambda tup: tup[-1])
    ]
    sorted_weights = [
        w for u, v, w in sorted(G3.edges(data="n_lines"), key=lambda tup: tup[-1])
    ]
    edge_widths_scene = [w / 150 for w in sorted_weights]
    vmin = min(edge_widths_scene)
    vmax = max(edge_widths_scene)

    fig, ax = plt.subplots(1, 1, figsize=(height + 1, height))
    labels = get_formatted_labels(G3, selected_labels)
    pos = nx.circular_layout(G3)

    nx.draw_networkx_edges(
        G3,
        pos=pos,
        ax=ax,
        edgelist=sorted_edges,
        width=edge_widths_scene,
        edge_cmap=cm.Reds,
        edge_vmin=vmin,
        edge_vmax=vmax,
        edge_color=edge_widths_scene,
    )
    position_full_radial_labels(G3, labels, pos)
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_ce-scene-mw.pdf",
        axis_off=True,
        tight=True,
    )

    # Radials for Act III only, with all named characters occurring in that act
