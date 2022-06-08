"""Parallel coordinate plotting script (ranking of characters)."""

import os
from glob import glob

import matplotlib.pyplot as plt
import pandas as pd
from cycler import cycler
from matplotlib import cm
from statics import DATA_PATH, GRAPHICS_PATH

from hyperbard.io import load_graph
from hyperbard.ranking import get_character_ranking
from hyperbard.utils import get_filename_base, get_name_from_identifier

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = "Palatino"
plt.rcParams["text.usetex"] = True
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["font.size"] = 29


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
        lw=3,
    )
    ax.invert_yaxis()
    labels = [
        get_name_from_identifier(elem.get_text()) for elem in ax.legend().get_texts()
    ]
    plt.xticks(rotation=45)
    legend = plt.legend(loc=(1.01, 0), labels=labels, ncol=2)
    frame = legend.get_frame()
    frame.set_edgecolor("black")
    frame.set_boxstyle("square", pad=0)
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, transparent=True, bbox_inches="tight", backend="pgf")
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
    se_speech_m = load_graph(play, "se-speech-mwd", "n_lines")

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
            "name": "07_se-scene-b",
            "graph": se_scene,
        },
        {
            "name": "08_se-scene-w",
            "graph": se_scene,
            "weight": "n_lines",
        },
        {
            "name": "09_se-group-b",
            "graph": se_group,
        },
        {
            "name": "10_se-group-w",
            "graph": se_group,
            "weight": "n_lines",
        },
        {
            "name": "11_se-speech-wd_in",
            "graph": se_speech,
            "weight": "n_lines",
            "degree": "in",
        },
        {
            "name": "12_se-speech-wd_out",
            "graph": se_speech,
            "weight": "n_lines",
            "degree": "out",
        },
        {
            "name": "13_se-speech-mwd_in",
            "graph": se_speech_m,
            "weight": "n_lines",
            "degree": "in",
        },
        {
            "name": "14_se-speech-mwd_out",
            "graph": se_speech_m,
            "weight": "n_lines",
            "degree": "out",
        },
    ]

    df_ranking = get_character_ranking(representations)

    plot_character_rankings(
        df_ranking,
        save_path=os.path.join(
            f"{GRAPHICS_PATH}", f"{play}_ranking_parallel_coordinates.pdf"
        ),
    )


if __name__ == "__main__":
    plays = [
        get_filename_base(fn).replace(".agg", "")
        for fn in sorted(glob(f"{DATA_PATH}/*.agg.csv"))
    ]

    for play in plays:
        handle_play(play)
