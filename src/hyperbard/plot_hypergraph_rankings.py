"""Plot ranking of characters for hypergraph representation."""

import os

import numpy as np
import pandas as pd

from glob import glob
from statics import (
    DATA_PATH,
    GRAPHICS_PATH
)

from cycler import cycler
from matplotlib import cm

from hyperbard.io import load_hypergraph
from hyperbard.plot_parallel_coordinates import plot_character_rankings
from hyperbard.ranking import get_character_ranking
from hyperbard.utils import (
    get_filename_base,
    get_name_from_identifier
)

import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = "Palatino"
plt.rcParams["text.usetex"] = True
plt.rcParams['pdf.fonttype'] = 42


def handle_play(play):
    print(play)

    hg_group_mw = load_hypergraph(play, "hg-group-mw", "n_lines")

    sublevel = [
        {
            "name": f"{i:02d}- $s \leq {i}$",
            "graph": hg_group_mw,
            "weight": "n_lines",
            "s": i,
            "superlevel": False,
        } for i in range(1, 7)
    ]

    superlevel = [
        {
            "name": f"{i + 6:02d}- $s \geq {i}$",
            "graph": hg_group_mw,
            "weight": "n_lines",
            "s": i,
            "superlevel": True,
        } for i in range(1, 7)
    ]

    representations = sublevel + superlevel
    df_ranking = get_character_ranking(representations)

    plot_character_rankings(
        df_ranking,
        save_path=os.path.join(
            f"{GRAPHICS_PATH}", f"{play}_hg_ranking_parallel_coordinates.pdf"
        )
    )

    return df_ranking


if __name__ == '__main__':
    plays = [
        get_filename_base(fn).replace('.agg', '')
        for fn in sorted(glob(f"{DATA_PATH}/*.agg.csv"))
    ]

    for play in plays:
        handle_play(play)
