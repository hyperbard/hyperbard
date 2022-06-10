"""Plot ranking of characters for hypergraph representation."""

import os
from glob import glob

import matplotlib.pyplot as plt
from statics import DATA_PATH, GRAPHICS_PATH

from hyperbard.graph_io import load_hypergraph
from hyperbard.plot_graph_rankings import plot_character_rankings
from hyperbard.plotting_utils import set_rcParams
from hyperbard.ranking import get_character_ranking
from hyperbard.utils import get_filename_base, remove_uppercase_prefixes

set_rcParams()


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
        }
        for i in range(1, 7)
    ]

    superlevel = [
        {
            "name": f"{i + 6:02d}- $s \geq {i}$",
            "graph": hg_group_mw,
            "weight": "n_lines",
            "s": i,
            "superlevel": True,
        }
        for i in range(1, 7)
    ]

    representations = sublevel + superlevel
    df_ranking = get_character_ranking(representations).rename(
        dict(index="node"), axis=1
    )
    df_ranking.node = df_ranking.node.map(remove_uppercase_prefixes)
    df_ranking = df_ranking.sort_values("node").rename(dict(node="index"), axis=1)

    plot_character_rankings(
        df_ranking,
        save_path=os.path.join(
            f"{GRAPHICS_PATH}", f"{play}_hg_ranking_parallel_coordinates.pdf"
        ),
    )

    return df_ranking


if __name__ == "__main__":
    plays = [
        get_filename_base(fn).replace(".agg", "")
        for fn in sorted(glob(f"{DATA_PATH}/*.agg.csv"))
    ]

    for play in plays:
        handle_play(play)
