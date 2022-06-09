import matplotlib.cm as cm
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

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


def position_full_radial_labels(G, labels, pos, fontsize):
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
        txt = ax.annotate(labels[n], pos_n, fontsize=fontsize, va=va, ha=ha)
        txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])


def position_partial_radial_labels(G, labels, pos, fontsize):
    for n in G.nodes():
        pos_n = pos[n]
        label_n = labels[n]
        if label_n in ["\\textbf{LadyCapulet}"]:
            pos_n[0] -= 0.2
        if label_n in ["Petrucio"]:
            pos_n[0] -= 0.1
        if label_n in ["PrinceEscalus"]:
            pos_n[0] += 0.2
        ha = "center"
        va = "center"
        txt = ax.annotate(labels[n], pos_n, fontsize=fontsize, va=va, ha=ha)
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
    position_full_radial_labels(G1, labels, pos, font_size + 6)
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
    position_full_radial_labels(G2, labels, pos, font_size + 6)
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_ce-scene-mb.pdf",
        axis_off=True,
        tight=True,
    )

    G3 = load_graph("romeo-and-juliet", "ce-scene-mw", edge_weights="n_lines")
    G3_for_drawing = weighted_multi_to_weighted_simple(G3, "n_lines")

    sorted_edges = [
        (u, v)
        for u, v, w in sorted(
            G3_for_drawing.edges(data="n_lines"), key=lambda tup: tup[-1]
        )
    ]
    sorted_weights = [
        w
        for u, v, w in sorted(
            G3_for_drawing.edges(data="n_lines"), key=lambda tup: tup[-1]
        )
    ]
    edge_widths_scene = [w / 150 for w in sorted_weights]
    vmin = min(edge_widths_scene)
    vmax = max(edge_widths_scene)

    fig, ax = plt.subplots(1, 1, figsize=(height + 1, height))
    labels = get_formatted_labels(G3_for_drawing, selected_labels)
    pos = nx.circular_layout(G3_for_drawing)

    nx.draw_networkx_edges(
        G3_for_drawing,
        pos=pos,
        ax=ax,
        edgelist=sorted_edges,
        width=edge_widths_scene,
        edge_cmap=cm.Reds,
        edge_vmin=vmin,
        edge_vmax=vmax,
        edge_color=edge_widths_scene,
    )
    position_full_radial_labels(G3_for_drawing, labels, pos, font_size + 6)
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_ce-scene-mw.pdf",
        axis_off=True,
        tight=True,
    )

    # Radials for Act III only, with all named characters occurring in that act
    act_three_edges = [
        (u, v, k) for u, v, k, d in G3.edges(keys=True, data=True) if d["act"] == 3
    ]
    G3_subgraph = G3.edge_subgraph(act_three_edges)
    G3_subgraph_for_drawing = weighted_multi_to_weighted_simple(G3_subgraph, "n_lines")
    sorted_edges = [
        (u, v)
        for u, v, w in sorted(
            G3_subgraph_for_drawing.edges(data="n_lines"), key=lambda tup: tup[-1]
        )
    ]
    sorted_weights = [
        w
        for u, v, w in sorted(
            G3_subgraph_for_drawing.edges(data="n_lines"), key=lambda tup: tup[-1]
        )
    ]
    edge_widths_scene = [w / 50 for w in sorted_weights]

    fig, ax = plt.subplots(1, 1, figsize=(height + 1, height))
    labels = get_formatted_labels(G3_subgraph_for_drawing, selected_labels)
    pos = nx.circular_layout(G3_subgraph_for_drawing)

    nx.draw_networkx_edges(
        G3_subgraph_for_drawing,
        pos=pos,
        ax=ax,
        edgelist=sorted_edges,
        width=edge_widths_scene,
        edge_cmap=cm.Reds,
        edge_vmin=min(edge_widths_scene),
        edge_vmax=max(edge_widths_scene),
        edge_color=edge_widths_scene,
    )
    position_partial_radial_labels(G3_subgraph_for_drawing, labels, pos, font_size)
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_ce-scene-mw-3.pdf",
        axis_off=True,
        tight=True,
    )

    G4 = load_graph("romeo-and-juliet", "ce-group-mw", edge_weights="n_lines")
    act_three_edges_group = [
        (u, v, k) for u, v, k, d in G4.edges(keys=True, data=True) if d["act"] == 3
    ]
    G4_subgraph = G4.edge_subgraph(act_three_edges_group)
    G4_subgraph_for_drawing = weighted_multi_to_weighted_simple(G4_subgraph, "n_lines")
    sorted_edges_G4 = [
        (u, v)
        for u, v, w in sorted(
            G4_subgraph_for_drawing.edges(data="n_lines"), key=lambda tup: tup[-1]
        )
    ]
    sorted_weights_G4 = [
        w
        for u, v, w in sorted(
            G4_subgraph_for_drawing.edges(data="n_lines"), key=lambda tup: tup[-1]
        )
    ]
    edge_widths_G4 = [w / 50 for w in sorted_weights_G4]

    fig, ax = plt.subplots(1, 1, figsize=(height + 1, height))
    labels = get_formatted_labels(G4_subgraph_for_drawing, selected_labels)
    pos = nx.circular_layout(G4_subgraph_for_drawing)

    nx.draw_networkx_edges(
        G4_subgraph_for_drawing,
        pos=pos,
        ax=ax,
        edgelist=sorted_edges_G4,
        width=edge_widths_G4,
        edge_cmap=cm.Reds,
        edge_vmin=min(edge_widths_G4),
        edge_vmax=max(edge_widths_G4),
        edge_color=edge_widths_G4,
    )
    position_partial_radial_labels(G4_subgraph_for_drawing, labels, pos, font_size)

    plt.axis("off")
    plt.tight_layout()
    save_pgf_fig(f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_ce-group-mw-3.pdf")

    df_diff = pd.DataFrame(
        sorted(G3_subgraph_for_drawing.edges(data="n_lines")),
        columns=["node1", "node2", "n_lines_scene"],
    ).set_index(["node1", "node2"])
    df_diff["n_lines_group"] = 0
    for n1, n2, w in G4_subgraph_for_drawing.edges(data="n_lines"):
        df_diff.at[(n1, n2), "n_lines_group"] = w
    df_diff["n_lines_difference"] = df_diff.n_lines_scene - df_diff.n_lines_group
    df_diff = df_diff.query("n_lines_difference != 0")
    edge_widths_difference = [
        df_diff.at[(u, v), "n_lines_difference"] / 50
        for u, v in G3_subgraph_for_drawing.edges()
        if (u, v) in df_diff.index
    ]

    fig, ax = plt.subplots(1, 1, figsize=(height + 1, height))
    pos = nx.circular_layout(G3_subgraph_for_drawing)
    nx.draw_networkx_edges(
        G3_subgraph_for_drawing,
        pos=pos,
        ax=ax,
        edgelist=df_diff.sort_values("n_lines_difference", ascending=True).index,
        width=sorted(edge_widths_difference),
        edge_cmap=cm.Blues,
        edge_vmin=min(edge_widths_difference),
        edge_vmax=max(edge_widths_difference),
        edge_color=sorted(edge_widths_difference),
    )

    position_partial_radial_labels(G3_subgraph_for_drawing, labels, pos, font_size)

    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_ce-3-differences.pdf",
        axis_off=True,
        tight=True,
    )

    # Star expansions for Act III only, with all named characters occurring in that act
