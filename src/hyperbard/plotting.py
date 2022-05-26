import os
from glob import glob
from itertools import product

import hypernetx as hnx
import numpy as np
import seaborn as sns

from hyperbard.ranking import get_character_ranking_df
from hyperbard.representations import get_hypergraph
from hyperbard.utils import split_identifier

sns.set_style("whitegrid")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm

from hyperbard.preprocessing import get_filename_base
from hyperbard.statics import DATA_PATH, GRAPHICS_PATH


def plot_character_rankings(df, save_path=None):
    """
    baby plotting function (wip!)
    """
    character_ranking_df = get_character_ranking_df(df)
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(
            3 * (len(character_ranking_df.columns) - 1),
            9 + len(character_ranking_df) // 10,
        ),
    )
    ax.set_prop_cycle(linestyle=["-", "--", ":", "-."], marker=["^", ">", "v", "<"])
    pd.plotting.parallel_coordinates(
        character_ranking_df,
        class_column="index",
        colormap=cm.viridis,
        ax=ax,
        alpha=0.5,
    )
    ax.invert_yaxis()
    labels = [split_identifier(elem.get_text()) for elem in ax.legend().get_texts()]
    plt.legend(loc=(1, 0), labels=labels)
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, transparent=True, bbox_inches="tight", backend="pgf")
        plt.close()


def plot_correlation_matrix(df, save_path=None):
    character_ranking_df = get_character_ranking_df(df)
    character_ranking_df_indexed = character_ranking_df.set_index("index")
    vmin = min(
        character_ranking_df_indexed.corr("spearman").min().min(),
        character_ranking_df_indexed.corr("kendall").min().min(),
    )
    sns.heatmap(
        character_ranking_df_indexed.corr("kendall"),
        square=True,
        cmap=cm.Reds,
        cbar_kws=dict(shrink=0.8),
        mask=np.tril(character_ranking_df_indexed.corr("kendall").values, k=0).astype(
            bool
        ),
        vmin=vmin,
        vmax=1.0,
        cbar=False,
    )
    sns.heatmap(
        character_ranking_df_indexed.corr("spearman"),
        square=True,
        cmap=cm.Reds,
        cbar_kws=dict(shrink=0.8),
        mask=np.triu(character_ranking_df_indexed.corr("spearman").values, k=0).astype(
            bool
        ),
        vmin=vmin,
        vmax=1.0,
    )
    plt.title("upper triangle: kendall, lower triangle: spearman")
    if save_path is not None:
        plt.savefig(save_path, transparent=True, backend="pgf", bbox_inches="tight")
        plt.close()


def plot_hypergraphs(df, groupby, separate="graph", save_path=None):
    H = get_hypergraph(df, groupby)
    layout_kwargs = {"layout_kwargs": {"seed": 1234}}
    if separate == "graph":
        hnx.draw(
            H,
            node_labels={n.uid: split_identifier(n.uid) for n in H.nodes()},
            node_radius=dict(
                (
                    df.groupby(["speaker"]).agg({"n_lines": "sum"}) / 200 + 1
                ).n_lines.items()
            ),
            with_edge_labels=False,
            edges_kwargs=dict(
                edgecolors=[cm.viridis_r(x / len(H)) for x in range(len(H))]
            ),
            **layout_kwargs,
        )
    elif separate == "act":
        acts = sorted(set(e.act for e in H.edges()))
        n_acts = len(acts)
        fig, ax = plt.subplots(1, n_acts, figsize=(n_acts * 5, 5))
        for act in acts:
            tax = ax[act - 1]
            tax.set_title(f"Act {act}")
            nH = H.restrict_to_edges([e for e in H.edges() if e.act == act])
            hnx.draw(
                nH,
                ax=tax,
                node_labels={n.uid: split_identifier(n.uid) for n in nH.nodes()},
                # TODO speaker can be list
                node_radius=dict(
                    (
                        df.query("act == @act")
                        .groupby(["speaker"])
                        .agg({"n_lines": "sum"})
                        / 25
                        + 1
                    ).n_lines.items()
                ),
                with_edge_labels=False,
                edges_kwargs=dict(
                    edgecolors=[cm.viridis_r(x / len(nH)) for x in range(len(nH))]
                ),
                **layout_kwargs,
            )
    elif separate == "scene":
        acts = sorted(set(e.act for e in H.edges()))
        n_acts = len(acts)
        scenes = sorted(set(e.scene for e in H.edges()))
        n_scenes = len(scenes)
        fig, ax = plt.subplots(n_scenes, n_acts, figsize=(n_acts * 5, n_scenes * 5))
        for act, scene in sorted(set((e.act, e.scene) for e in H.edges())):
            tax = ax[scene - 1][act - 1]
            tax.set_title(f"Act {act}, Scene {scene}")
            nH = H.restrict_to_edges(
                [e for e in H.edges() if e.act == act and e.scene == scene]
            )
            # TODO pull out drawing into function
            hnx.draw(
                nH,
                ax=tax,
                node_labels={n.uid: split_identifier(n.uid) for n in nH.nodes()},
                node_radius=dict(
                    (
                        df.query("act == @act and scene == @scene")
                        .groupby(["speaker"])
                        .agg({"n_lines": "sum"})
                        / 25
                        + 1
                    ).n_lines.items()
                ),
                with_edge_labels=False,
                edges_kwargs=dict(
                    edgecolors=[cm.viridis_r(x / len(nH)) for x in range(len(nH))]
                ),
                **layout_kwargs,
            )
        for x, y in product(list(range(n_scenes)), list(range(n_acts))):
            ax[x][y].axis("off")
    else:
        raise ValueError(
            f"separate={separate} but must be one of ['graph', 'act', 'scene']"
        )
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, transparent=True, backend="pgf", bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    files = sorted(glob(f"{DATA_PATH}/*agg.csv"))
    os.makedirs(GRAPHICS_PATH, exist_ok=True)
    for file in files:
        file_short = get_filename_base(file).split("_")[0]
        print(file_short)
        df = pd.read_csv(file)
        # file naming practice is file_short_{grouped by what}_{aggregated for viz into what}
        for groupby in [["act", "scene"], ["act", "scene", "stagegroup"]]:
            for separate in ["graph", "act"]:
                plot_hypergraphs(
                    df,
                    groupby,
                    separate=separate,
                    save_path=f"{GRAPHICS_PATH}/{file_short}_{'-'.join(groupby)}_{separate}.pdf",
                )
            if groupby == ["act", "scene", "stagegroup"]:
                separate = "scene"
                plot_hypergraphs(
                    df,
                    groupby,
                    separate=separate,
                    save_path=f"{GRAPHICS_PATH}/{file_short}_{'-'.join(groupby)}_{separate}.pdf",
                )
        plot_character_rankings(
            df,
            save_path=f"{GRAPHICS_PATH}/{file_short}_ranking_parallel_coordinates.pdf",
        )
        plot_correlation_matrix(
            df, save_path=f"{GRAPHICS_PATH}/{file_short}_ranking_correlations.pdf"
        )
