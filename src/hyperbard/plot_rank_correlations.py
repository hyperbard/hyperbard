from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from hyperbard.plotting_utils import set_rcParams
from hyperbard.statics import PAPERGRAPHICS_PATH, RANKINGDATA_PATH
from hyperbard.track_time import timeit


def get_correlation_dfs(ranking_files):
    dfs = dict()
    corrs = dict()
    for file in ranking_files:
        filename = file.split("/")[-1].split("_")[0]
        dfs[filename] = pd.read_csv(file, index_col=0)
        corrs[filename] = dfs[filename].corr()
    return corrs


def get_average_correlation(corrs):
    return sum(corrs.values()) / len(corrs)


def get_asymmetric_correlation_difference(first_corr_df, second_corr_df):
    return first_corr_df - second_corr_df


def plot_correlation_difference_matrix(
    selected_correlation, difference_correlation, selected_name
):
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    cax = inset_axes(
        ax,
        width="40%",
        height="10%",
        loc="lower left",
        bbox_to_anchor=(0, 1.1, 1, 1),
        bbox_transform=ax.transAxes,
        borderpad=0,
    )
    cax2 = inset_axes(
        ax,
        width="40%",
        height="10%",
        loc="lower right",
        bbox_to_anchor=(0, 1.1, 1, 1),
        bbox_transform=ax.transAxes,
        borderpad=0,
    )
    sns.heatmap(
        selected_correlation,
        square=True,
        cmap="Greys",
        mask=np.triu(selected_correlation, k=0),
        ax=ax,
        cbar_ax=cax,
        cbar_kws=dict(orientation="horizontal"),
    )
    g = sns.heatmap(
        difference_correlation,
        square=True,
        cmap="RdBu_r",
        vmin=-0.15,
        vmax=0.15,
        mask=np.tril(difference_correlation, k=0),
        ax=ax,
        cbar_ax=cax2,
        cbar_kws=dict(orientation="horizontal"),
        xticklabels=3,
    )
    g.get_xaxis().set_tick_params(rotation=0)
    cax2.get_xaxis().set_ticks(np.arange(-0.15, 0.16, 0.1))
    cax.get_xaxis().set_ticks(np.arange(0.7, 1.01, 0.1))
    cax.set_xlim(selected_correlation.min().min(), selected_correlation.max().max())
    cax2.set_xlim(-0.15, 0.15)
    plt.subplots_adjust(top=0.8)
    # pgf backend fails to plot second colorbar ticks - no idea why
    plt.savefig(
        f"{PAPERGRAPHICS_PATH}/{selected_name}_rank-correlations.pdf",
        transparent=True,
        bbox_inches="tight",
    )


@timeit
def plot_rank_correlations():
    ranking_files = sorted(glob(f"{RANKINGDATA_PATH}/**_ranking.csv"))
    corrs = get_correlation_dfs(ranking_files)
    average_correlation = get_average_correlation(corrs)
    randj_correlation = corrs["romeo-and-juliet"]
    diff_correlation = get_asymmetric_correlation_difference(
        randj_correlation, average_correlation
    )
    plot_correlation_difference_matrix(
        randj_correlation, diff_correlation, "romeo-and-juliet"
    )


if __name__ == "__main__":
    set_rcParams(26)
    plot_rank_correlations()
