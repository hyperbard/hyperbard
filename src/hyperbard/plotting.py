from glob import glob

import numpy as np
import seaborn as sns

from hyperbard.ranking import get_character_ranking_df
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


if __name__ == "__main__":
    files = sorted(glob(f"{DATA_PATH}/*agg.csv"))
    for file in files:
        file_short = get_filename_base(file).split("_")[0]
        print(file_short)
        df = pd.read_csv(file)
        plot_character_rankings(
            df,
            save_path=f"{GRAPHICS_PATH}/{file_short}_ranking_parallel_coordinates.pdf",
        )
        plot_correlation_matrix(
            df, save_path=f"{GRAPHICS_PATH}/{file_short}_ranking_correlations.pdf"
        )
