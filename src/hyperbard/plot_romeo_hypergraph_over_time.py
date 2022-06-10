import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from hyperbard.plotting_utils import get_character_color, save_pgf_fig
from hyperbard.statics import GRAPHDATA_PATH, PAPERGRAPHICS_PATH
from hyperbard.utils import get_name_from_identifier


def plot_romeo_hypergraph_over_time(selected_labels, font_size):
    hg_speech_mwd = pd.read_csv(
        f"{GRAPHDATA_PATH}/romeo-and-juliet_hg-speech-mwd.edges.csv"
    )
    hg_speech_mwd.speaker = hg_speech_mwd.speaker.map(
        lambda x: [
            y
            for y in map(get_name_from_identifier, x.split())
            if not y.isupper() and not y.startswith("SERVANT")
        ]
    )
    hg_speech_mwd.onstage = hg_speech_mwd.onstage.map(
        lambda x: [
            y
            for y in map(get_name_from_identifier, x.split())
            if not y.isupper() and not y.startswith("SERVANT")
        ]
    )
    hg_speech_mwd["n_lines_cumulative"] = hg_speech_mwd.n_lines.cumsum()
    hg_speech_mwd_exploded_speaker = hg_speech_mwd.explode("speaker")
    speaker_df = pd.DataFrame(
        index=sorted({elem for sublist in hg_speech_mwd.speaker for elem in sublist}),
        columns=hg_speech_mwd.n_lines_cumulative,
    )
    for line in hg_speech_mwd.n_lines_cumulative:
        queried = (
            hg_speech_mwd_exploded_speaker.query("n_lines_cumulative <= @line")
            .groupby("speaker")
            .agg(dict(n_lines=sum))
        )
        for idx, n_lines in queried.n_lines.items():
            speaker_df.at[idx, line] = n_lines / line
    transformed_df = speaker_df.T[
        [x for x in speaker_df.index if x != "Chorus"]
    ].fillna(0)

    fig, ax = plt.subplots(1, 1, figsize=(16, 7))
    ax.vlines(
        x=[
            hg_speech_mwd.query("act == @act").n_lines_cumulative.max()
            for act in range(0, 5)
        ],
        lw=1,
        ymin=0,
        ymax=0.25,
        colors="k",
        linestyles="--",
    )
    transformed_df[
        [c for c in transformed_df.columns if c not in selected_labels]
    ].plot.line(
        ax=ax,
        color={k: get_character_color(k) for k in transformed_df.columns},
        lw=1,
        linestyle="-",
        legend=False,
    )
    transformed_df[sorted(selected_labels)].plot.line(
        ax=ax,
        color={k: get_character_color(k) for k in transformed_df.columns},
        linestyle="-",
        lw=3,
    )
    sns.despine(offset=0, trim=True)
    handles, labels = ax.get_legend_handles_labels()
    plt.xticks(
        range(0, hg_speech_mwd.n_lines_cumulative.max(), 500),
        fontsize=font_size,
    )
    plt.yticks(np.arange(0, 0.26, 0.05), fontsize=font_size)
    legend = ax.legend(
        handles=handles[-5:],
        labels=labels[-5:],
        loc=(1.001, 0.535),
        fontsize=font_size,
    )
    frame = legend.get_frame()
    frame.set_edgecolor("black")
    frame.set_boxstyle("square", pad=0)
    # plt.tight_layout()
    plt.xlabel("Number of lines spoken", fontsize=font_size, labelpad=9)
    plt.ylabel("Fraction of lines spoken", fontsize=font_size, labelpad=15)
    save_pgf_fig(
        f"{PAPERGRAPHICS_PATH}/romeo_and_juliet_hg-speech-over-time.pdf",
        axis_off=False,
        tight=True,
    )
