from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from hyperbard.plotting_utils import set_rcParams
from hyperbard.statics import PAPERGRAPHICS_PATH, RANKINGDATA_PATH

set_rcParams(26)

ranking_files = sorted(glob(f"{RANKINGDATA_PATH}/**_ranking.csv"))

dfs = dict()
corrs = dict()
for file in ranking_files:
    filename = file.split("/")[-1].split("_")[0]
    dfs[filename] = pd.read_csv(file, index_col=0)
    corrs[filename] = dfs[filename].corr()

average_correlation = sum(corrs.values()) / len(corrs)
randj_correlation = corrs["romeo-and-juliet"]
diff_correlation = randj_correlation - average_correlation

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
    randj_correlation,
    square=True,
    cmap="Greys",
    mask=np.triu(diff_correlation, k=0),
    ax=ax,
    cbar_ax=cax,
    cbar_kws=dict(orientation="horizontal"),
)
g = sns.heatmap(
    diff_correlation,
    square=True,
    cmap="RdBu_r",
    vmin=-0.15,
    vmax=0.15,
    mask=np.tril(diff_correlation, k=0),
    ax=ax,
    cbar_ax=cax2,
    cbar_kws=dict(orientation="horizontal"),
    xticklabels=3,
)
g.get_xaxis().set_tick_params(rotation=0)
cax2.get_xaxis().set_ticks(np.arange(-0.15, 0.16, 0.1))
cax.get_xaxis().set_ticks(np.arange(0.7, 1.01, 0.1))
cax.set_xlim(randj_correlation.min().min(), randj_correlation.max().max())
cax2.set_xlim(-0.15, 0.15)
plt.subplots_adjust(top=0.8)
# pgf backend fails to plot second colorbar ticks - no idea why
plt.savefig(
    f"{PAPERGRAPHICS_PATH}/romeo-and-juliet_rank-correlations.pdf",
    transparent=True,
    bbox_inches="tight",
)
