import matplotlib.cm as cm
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from hyperbard.graph_io import load_graph
from hyperbard.plotting_utils import save_pgf_fig, set_rcParams
from hyperbard.statics import GRAPHDATA_PATH, PAPERGRAPHICS_PATH


# TODO fix
def prettify_identifier(identifier):
    return identifier.replace("#", "").split("_")[0]


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


def position_bipartite_labels(G, pos, labels, fontsize):
    for n in G.nodes():
        pos_n = pos[n]
        label_n = labels[n]
        if pos_n[0] == 0:
            ha = "right"
        else:
            ha = "left"
        va = "center"
        txt = ax.annotate(label_n, pos_n, fontsize=fontsize, va=va, ha=ha)
        txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])


def make_label(label):
    components = [int(x) for x in label.split(".")]
    return components


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
    position_partial_radial_labels(G3_subgraph_for_drawing, labels, pos, font_size + 6)
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
    position_partial_radial_labels(G4_subgraph_for_drawing, labels, pos, font_size + 6)

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

    position_partial_radial_labels(G3_subgraph_for_drawing, labels, pos, font_size + 6)

    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_ce-3-differences.pdf",
        axis_off=True,
        tight=True,
    )

    # Star expansions for Act III only, with all named characters occurring in that act
    G1 = load_graph("romeo-and-juliet", "se-scene-w", "n_lines")
    act_three_edges_scene = [
        (u, v) for u, v in G1.edges() if u.startswith("3") or v.startswith("3")
    ]
    G1_subgraph = G1.edge_subgraph(act_three_edges_scene)

    G2 = load_graph("romeo-and-juliet", "se-group-w", "n_lines")
    act_three_edges_group = [
        (u, v) for u, v in G2.edges() if u.startswith("3") or v.startswith("3")
    ]
    G2_subgraph = G2.edge_subgraph(act_three_edges_group)

    characters_act3 = sorted(
        {n for n, t in G1_subgraph.nodes(data="node_type") if t == "character"}
    )
    scene_play_parts_act3 = sorted(
        {n for n, t in G1_subgraph.nodes(data="node_type") if t == "text_unit"}
    )
    group_play_parts_act3 = sorted(
        {n for n, t in G2_subgraph.nodes(data="node_type") if t == "text_unit"}
    )

    pos = {
        **{
            k: (0, 1 - idx / (len(characters_act3) - 1))
            for idx, k in enumerate(characters_act3)
        },
        **{
            k: (1, 1 - idx / (len(scene_play_parts_act3) - 1))
            for idx, k in enumerate(scene_play_parts_act3)
        },
    }

    labels = {
        **{
            n: n.split(".")[-1]
            if n not in selected_labels
            else r"\textbf{" + n.split(".")[-1] + "}"
            for n in characters_act3
        },
        **{n: n.replace("3.0", "3.") for n in scene_play_parts_act3},
    }

    fig, ax = plt.subplots(1, 1, figsize=(6 - 1, 6))

    act3_edgewidths = [
        w / 75
        for u, v, w in sorted(
            G1_subgraph.edges(data="n_lines"), key=lambda tup: tup[-1]
        )
    ]
    min3 = min(act3_edgewidths)
    max3 = max(act3_edgewidths)
    nx.draw_networkx_edges(
        G1_subgraph,
        pos=pos,
        width=act3_edgewidths,
        edgelist=[
            (u, v)
            for u, v, w in sorted(
                G1_subgraph.edges(data="n_lines"), key=lambda tup: tup[-1]
            )
        ],
        edge_cmap=cm.Reds,
        edge_vmin=min3 - 5,
        edge_vmax=max3,
        edge_color=act3_edgewidths,
    )
    position_bipartite_labels(G1_subgraph, pos, labels, font_size + 6)

    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_se-scene_act-3.pdf",
        axis_off=True,
        tight=True,
    )

    bipartite_labels = {
        **{
            n: n.split(".")[-1]
            if n not in selected_labels
            else r"\textbf{" + n.split(".")[-1] + "}"
            for n in characters_act3
        },
        **{n: make_label(n) for n in group_play_parts_act3},
    }
    min_label = min([n[-1] for n in bipartite_labels.values() if type(n) == list])
    for k, v in bipartite_labels.items():
        if type(v) == list:
            bipartite_labels[k][-1] -= min_label - 1
            bipartite_labels[
                k
            ] = f"{bipartite_labels[k][0]}.{bipartite_labels[k][1]}.{bipartite_labels[k][-1]:02}"

    pos = {
        **{
            k: (0, 1 - idx / (len(characters_act3) - 1))
            for idx, k in enumerate([l for l in bipartite_labels if l[0].isalpha()])
        },
        **{
            k: (1, 1 - idx / (len(group_play_parts_act3) - 1))
            for idx, k in enumerate([l for l in bipartite_labels if l[0].isdigit()])
        },
    }

    font_size = 16
    fig, ax = plt.subplots(1, 1, figsize=(6 - 1, 6))
    act3_group_edgewidths = [
        w / (75 / 2)
        for u, v, w in sorted(
            G2_subgraph.edges(data="n_lines"), key=lambda tup: tup[-1]
        )
    ]
    min3 = min(act3_group_edgewidths)
    max3 = max(act3_group_edgewidths)
    nx.draw_networkx_edges(
        G2_subgraph,
        pos=pos,
        width=act3_group_edgewidths,
        edgelist=[
            (u, v)
            for u, v, w in sorted(
                G2_subgraph.edges(data="n_lines"), key=lambda tup: tup[-1]
            )
        ],
        edge_cmap=cm.Reds,
        edge_vmin=min3,
        edge_vmax=max3,
        edge_color=act3_group_edgewidths,
    )
    for n in G2_subgraph.nodes():
        pos_n = pos[n]
        label_n = bipartite_labels[n]
        if pos_n[0] == 0:
            ha = "right"
            fontsize = font_size + 6
        else:
            ha = "left"
            fontsize = font_size
        va = "center"
        txt = ax.annotate(bipartite_labels[n], pos_n, fontsize=fontsize, va=va, ha=ha)
        txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_se-group_act-3.pdf",
        axis_off=True,
        tight=True,
    )

    # TODO refactor to use graph loader
    speech_nodes = pd.read_csv(f"{GRAPHDATA_PATH}/romeo-and-juliet_se-speech.nodes.csv")
    speech_nodes.node = speech_nodes.node.map(prettify_identifier)
    speech_edges_wd = pd.read_csv(
        f"{GRAPHDATA_PATH}/romeo-and-juliet_se-speech-wd.edges.csv"
    )
    speech_edges_wd.source = speech_edges_wd.source.map(prettify_identifier)
    speech_edges_wd.target = speech_edges_wd.target.map(prettify_identifier)
    speech_edges_wd_3_5 = speech_edges_wd.query(
        "source.str.startswith('3.') or target.str.startswith('3.')"
    ).copy()
    speech_edges_wd_3_5 = speech_edges_wd_3_5.query(
        "not source.str.isupper() and not target.str.isupper()"
    ).copy()
    speech_edges_wd_3_5.source = speech_edges_wd_3_5.source.map(
        lambda x: x if x.startswith("3") else f"{x}-O"
    )
    speech_edges_wd_3_5.target = speech_edges_wd_3_5.target.map(
        lambda x: x if x.startswith("3") else f"{x}-I"
    )
    speech_G = nx.DiGraph()
    speech_G.add_nodes_from(
        {n for n in list(speech_edges_wd_3_5.source) + list(speech_edges_wd_3_5.target)}
    )
    speech_G.add_weighted_edges_from(
        list(
            zip(
                speech_edges_wd_3_5.source,
                speech_edges_wd_3_5.target,
                speech_edges_wd_3_5.n_lines,
            )
        )
    )
    in_characters = sorted([n for n in speech_G.nodes if n.endswith("I")])
    out_characters = sorted([n for n in speech_G.nodes if n.endswith("O")])
    text_units = sorted([n for n in speech_G.nodes if n.startswith("3")])

    pos = {
        **{
            k: (0, 1 - idx / (len(out_characters) - 1))
            for idx, k in enumerate(out_characters)
        },
        **{k: (1, 1 - idx / (len(text_units) - 1)) for idx, k in enumerate(text_units)},
        **{
            k: (2, 1 - idx / (len(in_characters) - 1))
            for idx, k in enumerate(in_characters)
        },
    }

    font_size = 16
    fig, ax = plt.subplots(1, 1, figsize=(6 + 2, 6))
    speech_edgewidths = [
        w / (75 / 2)
        for u, v, w in sorted(speech_G.edges(data="weight"), key=lambda tup: tup[-1])
    ]
    speech_edgewidths_out = [
        w / (75 / 2)
        for u, v, w in sorted(speech_G.edges(data="weight"), key=lambda tup: tup[-1])
        if u.endswith("O")
    ]
    speech_edgewidths_in = [
        w / (75 / 2)
        for u, v, w in sorted(speech_G.edges(data="weight"), key=lambda tup: tup[-1])
        if v.endswith("I")
    ]
    min3 = min(speech_edgewidths)
    max3 = max(speech_edgewidths)
    nx.draw_networkx_edges(
        speech_G,
        pos=pos,
        width=speech_edgewidths_out,
        edgelist=[
            (u, v)
            for u, v, w in sorted(
                speech_G.edges(data="weight"), key=lambda tup: tup[-1]
            )
            if u.endswith("O")
        ],
        edge_cmap=cm.Reds,
        edge_vmin=min3,
        edge_vmax=max3,
        edge_color=speech_edgewidths_out,
        arrows=True,
        arrowstyle="wedge",
    )
    nx.draw_networkx_edges(
        speech_G,
        pos=pos,
        width=speech_edgewidths_in,
        edgelist=[
            (u, v)
            for u, v, w in sorted(
                speech_G.edges(data="weight"), key=lambda tup: tup[-1]
            )
            if v.endswith("I")
        ],
        edge_cmap=cm.Blues,
        edge_vmin=min3,
        edge_vmax=max3,
        edge_color=speech_edgewidths_in,
        arrows=True,
        arrowstyle="wedge",
    )
    for n in speech_G.nodes():
        pos_n = pos[n]
        label_n = bipartite_labels[n.split("-")[0]]
        if pos_n[0] == 0:
            ha = "right"
            fontsize = font_size + 6
        elif pos_n[0] == 2:
            ha = "left"
            fontsize = font_size + 6
        else:
            ha = "center"
            fontsize = font_size
        va = "center"
        txt = ax.annotate(label_n, pos_n, fontsize=fontsize, va=va, ha=ha)
        txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_se-speech_3.pdf",
        axis_off=True,
        tight=True,
    )
