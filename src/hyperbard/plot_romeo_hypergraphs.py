import hypernetx as hnx
import matplotlib.patheffects as PathEffects
import networkx as nx
import pandas as pd
from graph_io import load_hypergraph
from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.text import Annotation

from hyperbard.plotting_utils import save_pgf_fig
from hyperbard.statics import GRAPHDATA_PATH, PAPERGRAPHICS_PATH
from hyperbard.utils import get_name_from_identifier


def draw_hypergraph(H, node_radius, edge_width, fontsize, tax, layout_kwargs):
    pos = nx.spring_layout(H.bipartite(), **layout_kwargs["layout_kwargs"])
    min_edge_label = min(H.edges)
    edge_labels = {k: (k - min_edge_label + 1) for k in H.edges}
    node_labels = {k: get_name_from_identifier(k) for k in H.nodes}
    hnx.draw(
        H,
        ax=tax,
        pos=pos,
        with_node_labels=True,
        node_radius=node_radius,
        node_labels=node_labels,
        with_edge_labels=True,
        edge_labels=edge_labels,
        edges_kwargs=dict(
            edgecolors=[
                cm.viridis_r(x / H.number_of_edges())
                for x in range(H.number_of_edges())
            ],
            lw=edge_width,
            dr=0.05,
        ),
        edge_labels_kwargs=dict(fontsize=fontsize),
        node_labels_kwargs=dict(fontsize=fontsize),
        label_alpha=0,
    )
    for child in tax.get_children():
        if isinstance(child, Annotation):
            child.set_path_effects(
                [PathEffects.withStroke(linewidth=5, foreground="w")]
            )


def plot_romeo_hypergraphs():
    H = load_hypergraph("romeo-and-juliet", "hg-group-mw")
    hyperedges_act_three = [e for e in H.edges() if e.act == 3]
    node_weights_act_three = pd.read_csv(
        f"{GRAPHDATA_PATH}/romeo-and-juliet_hg-group-mw.node-weights.csv"
    ).query("act == 3")
    seed = 5
    for scene in range(1, 6):
        scene_edges = [e for e in hyperedges_act_three if e.scene == scene]
        H3 = H.restrict_to_edges(scene_edges)
        node_weights_scene = node_weights_act_three.query("scene == @scene")
        node_weights_scene = node_weights_scene.groupby("node").agg(
            dict(n_lines_speaker=sum)
        )
        radii3 = {
            k: v / (50 / 3)
            for k, v in zip(
                node_weights_scene.index, node_weights_scene.n_lines_speaker
            )
        }
        edge_width3 = {k.uid: k.n_lines / (50 / 3) for k in H3.edges()}

        seed = 11
        fontsize = 45 if scene in [2, 3, 4] else 30
        layout_kwargs = {"layout_kwargs": {"seed": seed}}
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
        draw_hypergraph(H3, radii3, edge_width3, fontsize + 6, ax, layout_kwargs)
        save_pgf_fig(
            f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_hg-group_3-{scene}.pdf",
            axis_off=False,
            tight=True,
        )
        plt.close()
