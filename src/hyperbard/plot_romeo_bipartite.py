import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import cm
from matplotlib import patheffects as PathEffects

from hyperbard.graph_io import load_graph
from hyperbard.plotting_utils import save_pgf_fig
from hyperbard.statics import PAPERGRAPHICS_PATH
from hyperbard.utils import remove_uppercase_prefixes


def make_label(label):
    components = [int(x) for x in label.split(".")]
    return components


def plot_romeo_bipartite(selected_labels, font_size):
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
            n: remove_uppercase_prefixes(n)
            if n not in selected_labels
            else r"\textbf{" + remove_uppercase_prefixes(n) + "}"
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
    position_bipartite_labels(G1_subgraph, pos, ax, labels, font_size)

    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_se-scene_act-3.pdf",
        axis_off=True,
        tight=True,
    )

    bipartite_labels = {
        **{
            n: remove_uppercase_prefixes(n)
            if n not in selected_labels
            else r"\textbf{" + remove_uppercase_prefixes(n) + "}"
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
            for idx, k in enumerate([l for l in bipartite_labels if l[0] == "#"])
        },
        **{
            k: (1, 1 - idx / (len(group_play_parts_act3) - 1))
            for idx, k in enumerate([l for l in bipartite_labels if l[0].isdigit()])
        },
    }

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
            fontsize = font_size
        else:
            ha = "left"
            fontsize = font_size - 6
        va = "center"
        txt = ax.annotate(label_n, pos_n, fontsize=fontsize, va=va, ha=ha)
        txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_se-group_act-3.pdf",
        axis_off=True,
        tight=True,
    )
    #
    # # TODO refactor to use graph loader
    # speech_nodes = pd.read_csv(f"{GRAPHDATA_PATH}/romeo-and-juliet_se-speech.nodes.csv")
    # speech_nodes.node = speech_nodes.node.map(get_name_from_identifier)
    # speech_edges_wd = pd.read_csv(
    #     f"{GRAPHDATA_PATH}/romeo-and-juliet_se-speech-wd.edges.csv"
    # )
    # speech_edges_wd.source = speech_edges_wd.source.map(get_name_from_identifier)
    # speech_edges_wd.target = speech_edges_wd.target.map(get_name_from_identifier)
    # speech_edges_wd_3_5 = speech_edges_wd.query(
    #     "source.str.startswith('3.') or target.str.startswith('3.')"
    # ).copy()
    # speech_edges_wd_3_5 = speech_edges_wd_3_5.query(
    #     "not source.str.isupper() and not target.str.isupper()"
    # ).copy()
    # speech_edges_wd_3_5.source = speech_edges_wd_3_5.source.map(
    #     lambda x: x if x.startswith("3") else f"{x}-O"
    # )
    # speech_edges_wd_3_5.target = speech_edges_wd_3_5.target.map(
    #     lambda x: x if x.startswith("3") else f"{x}-I"
    # )
    # speech_G = nx.DiGraph()
    # speech_G.add_nodes_from(
    #     {n for n in list(speech_edges_wd_3_5.source) + list(speech_edges_wd_3_5.target)}
    # )
    # speech_G.add_weighted_edges_from(
    #     list(
    #         zip(
    #             speech_edges_wd_3_5.source,
    #             speech_edges_wd_3_5.target,
    #             speech_edges_wd_3_5.n_lines,
    #         )
    #     )
    # )
    # in_characters = sorted([n for n in speech_G.nodes if n.endswith("I")])
    # out_characters = sorted([n for n in speech_G.nodes if n.endswith("O")])
    # text_units = sorted([n for n in speech_G.nodes if n.startswith("3")])
    #
    # pos = {
    #     **{
    #         k: (0, 1 - idx / (len(out_characters) - 1))
    #         for idx, k in enumerate(out_characters)
    #     },
    #     **{k: (1, 1 - idx / (len(text_units) - 1)) for idx, k in enumerate(text_units)},
    #     **{
    #         k: (2, 1 - idx / (len(in_characters) - 1))
    #         for idx, k in enumerate(in_characters)
    #     },
    # }
    #
    # fig, ax = plt.subplots(1, 1, figsize=(6 + 2, 6))
    # speech_edgewidths = [
    #     w / (75 / 2)
    #     for u, v, w in sorted(speech_G.edges(data="weight"), key=lambda tup: tup[-1])
    # ]
    # speech_edgewidths_out = [
    #     w / (75 / 2)
    #     for u, v, w in sorted(speech_G.edges(data="weight"), key=lambda tup: tup[-1])
    #     if u.endswith("O")
    # ]
    # speech_edgewidths_in = [
    #     w / (75 / 2)
    #     for u, v, w in sorted(speech_G.edges(data="weight"), key=lambda tup: tup[-1])
    #     if v.endswith("I")
    # ]
    # min3 = min(speech_edgewidths)
    # max3 = max(speech_edgewidths)
    # nx.draw_networkx_edges(
    #     speech_G,
    #     pos=pos,
    #     width=speech_edgewidths_out,
    #     edgelist=[
    #         (u, v)
    #         for u, v, w in sorted(
    #             speech_G.edges(data="weight"), key=lambda tup: tup[-1]
    #         )
    #         if u.endswith("O")
    #     ],
    #     edge_cmap=cm.Reds,
    #     edge_vmin=min3,
    #     edge_vmax=max3,
    #     edge_color=speech_edgewidths_out,
    #     arrows=True,
    #     arrowstyle="wedge",
    # )
    # nx.draw_networkx_edges(
    #     speech_G,
    #     pos=pos,
    #     width=speech_edgewidths_in,
    #     edgelist=[
    #         (u, v)
    #         for u, v, w in sorted(
    #             speech_G.edges(data="weight"), key=lambda tup: tup[-1]
    #         )
    #         if v.endswith("I")
    #     ],
    #     edge_cmap=cm.Blues,
    #     edge_vmin=min3,
    #     edge_vmax=max3,
    #     edge_color=speech_edgewidths_in,
    #     arrows=True,
    #     arrowstyle="wedge",
    # )
    # for n in speech_G.nodes():
    #     pos_n = pos[n]
    #     label_n = bipartite_labels[n.split("-")[0]]
    #     if pos_n[0] == 0:
    #         ha = "right"
    #         fontsize = font_size
    #     elif pos_n[0] == 2:
    #         ha = "left"
    #         fontsize = font_size
    #     else:
    #         ha = "center"
    #         fontsize = font_size - 6
    #     va = "center"
    #     txt = ax.annotate(label_n, pos_n, fontsize=fontsize, va=va, ha=ha)
    #     txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])
    # save_pgf_fig(
    #     f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_se-speech_3.pdf",
    #     axis_off=True,
    #     tight=True,
    # )


def position_bipartite_labels(G, pos, ax, labels, fontsize):
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
