"""Parallel coordinate plotting script (ranking of characters)."""

import os
from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from cycler import cycler
from matplotlib import cm
from statics import DATA_PATH, GRAPHICS_PATH, RANKINGDATA_PATH

from hyperbard.graph_io import load_graph
from hyperbard.plotting_utils import set_rcParams
from hyperbard.ranking import get_character_ranking
from hyperbard.utils import get_filename_base, remove_uppercase_prefixes

set_rcParams(29)


def plot_character_rankings(character_ranking_df, save_path=None):
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(
            2 * (len(character_ranking_df.columns) - 1),
            9 + len(character_ranking_df) // 10,
        ),
    )
    custom_cycler = cycler(linestyle=["-", "--", ":", "-."]) * cycler(
        marker=["^", ">", "v", "<"]
    )
    cmap = lambda i: cm.tab20c(i) if i % 2 == 0 else cm.tab20b(i)
    ax.set_prop_cycle(custom_cycler)
    pd.plotting.parallel_coordinates(
        character_ranking_df,
        class_column="index",
        colormap=cmap,
        ax=ax,
        alpha=0.8,
        lw=4,
        sort_labels=True,
        markersize=10,
    )
    ax.invert_yaxis()
    labels = [
        remove_uppercase_prefixes(elem.get_text()) for elem in ax.legend().get_texts()
    ]
    plt.xticks(rotation=45)
    legend = plt.legend(loc=(1.01, 0), labels=labels, ncol=2)
    frame = legend.get_frame()
    frame.set_edgecolor("black")
    frame.set_boxstyle("square", pad=0)
    # plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, transparent=True, bbox_inches="tight", backend="pgf")
        plt.close()
    else:
        plt.show()


def plot_correlation_matrices(lower, upper, lower_name, upper_name, save_path=None):
    vmin = min(upper.min().min(), lower.min().min())

    sns.heatmap(
        upper,
        square=True,
        cmap=cm.RdYlGn,
        cbar_kws=dict(shrink=0.8),
        mask=np.tril(upper, k=0).astype(bool),
        vmin=vmin,
        vmax=1.0,
        cbar=False,
    )
    sns.heatmap(
        lower,
        square=True,
        cmap=cm.Greys,
        cbar_kws=dict(shrink=0.8),
        mask=np.triu(lower.values, k=0).astype(bool),
        vmin=vmin,
        vmax=1.0,
    )

    plt.title(f"lower triangle: {lower_name}, upper triangle: {upper_name}")

    if save_path is not None:
        plt.savefig(save_path, transparent=True, backend="pgf", bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def handle_play(play):
    print(play)

    ce_scene_b = load_graph(play, "ce-scene-w", "count")
    ce_scene_m = load_graph(play, "ce-scene-mw", "n_lines")

    ce_group_b = load_graph(play, "ce-group-w", "count")
    ce_group_m = load_graph(play, "ce-group-mw", "n_lines")

    se_scene = load_graph(play, "se-scene-w", "n_lines")
    se_group = load_graph(play, "se-group-w", "n_lines")

    se_speech = load_graph(play, "se-speech-wd", "n_lines")

    representations = [
        {
            "name": "01-ce-scene-b",
            "graph": ce_scene_b,
        },
        {
            "name": "02-ce-scene-mb",
            "graph": ce_scene_b,
            "weight": "count",
        },
        {
            "name": "03-ce-scene-mw",
            "graph": ce_scene_m,
            "weight": "n_lines",
        },
        {
            "name": "04-ce-group-b",
            "graph": ce_group_b,
        },
        {
            "name": "05-ce-group-mb",
            "graph": ce_group_b,
            "weight": "count",
        },
        {
            "name": "06-ce-group-mw",
            "graph": ce_group_m,
            "weight": "n_lines",
        },
        {
            "name": "07-se-scene-b",
            "graph": se_scene,
        },
        {
            "name": "08-se-scene-w",
            "graph": se_scene,
            "weight": "n_lines",
        },
        {
            "name": "09-se-group-b",
            "graph": se_group,
        },
        {
            "name": "10-se-group-w",
            "graph": se_group,
            "weight": "n_lines",
        },
        {
            "name": "11-se-speech-wd_in",
            "graph": se_speech,
            "weight": "n_lines",
            "degree": "in",
        },
        {
            "name": "12-se-speech-wd_out",
            "graph": se_speech,
            "weight": "n_lines",
            "degree": "out",
        },
    ]

    df_ranking = get_character_ranking(representations)
    df_ranking = get_character_ranking(representations).rename(
        dict(index="node"), axis=1
    )
    df_ranking.node = df_ranking.node.map(remove_uppercase_prefixes)
    df_ranking = df_ranking.sort_values("node").rename(dict(node="index"), axis=1)

    plot_character_rankings(
        df_ranking,
        save_path=os.path.join(
            f"{GRAPHICS_PATH}", f"{play}_ranking_parallel_coordinates.pdf"
        ),
    )

    return df_ranking


def calculate_correlation_matrices(rankings):
    """Calculate correlation matrices from dictionary of data frames."""
    correlation_matrices = {}

    for play, ranking in rankings.items():
        ranking = ranking.set_index("index")
        correlations = ranking.corr("spearman")

        correlation_matrices[play] = correlations

    return correlation_matrices


if __name__ == "__main__":
    os.makedirs(GRAPHICS_PATH, exist_ok=True)
    os.makedirs(RANKINGDATA_PATH, exist_ok=True)

    plays = [
        get_filename_base(fn).replace(".agg", "")
        for fn in sorted(glob(f"{DATA_PATH}/*.agg.csv"))
    ]

    # Store rankings for subsequent comparison
    rankings = {}

    for play in plays:
        df_ranking = handle_play(play)

        df_ranking.to_csv(
            os.path.join(f"{RANKINGDATA_PATH}", f"{play}_ranking.csv"), index=False
        )

        rankings[play] = df_ranking
