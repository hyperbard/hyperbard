"""Simple summary statistics for hypergraphs."""

import argparse
import collections

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from hypernetx.algorithms.s_centrality_measures import s_eccentricity

from hyperbard.representations import get_hypergraph
from hyperbard.statics import META_PATH
from hyperbard.utils import get_filename_base

NAME_TO_TYPE = pd.read_csv(f"{META_PATH}/playtypes.csv").set_index("play_name")


def calculate_summary_statistics(name, hypergraphs, aggregate_fn=np.mean):
    """Given a set of hypergraphs, calculate summary statistics.

    This function will create a single row of a larger data frame,
    ultimately comprising more than one set of stats for one play.
    """
    data = collections.defaultdict(list)

    for k, v in hypergraphs.items():
        # TODO: go deeper/higher? I have not yet found a way to query
        # the hypergraph about its maximum $s$-connectivity.
        for s in [1, 2, 5]:
            eccentricity = s_eccentricity(v, s=s, edges=False)
            eccentricity = np.asarray(list(eccentricity.values()))
            eccentricity = np.mean(eccentricity)

            data[f"{s}_eccentricity"].append(eccentricity)

        data["n_nodes"].append(v.number_of_nodes())
        data["n_edges"].append(v.number_of_edges())
        data["avg_degree"].append(np.mean([v.degree(n) for n in v.nodes]))

    row = {
        "play": [name],
        "type": [NAME_TO_TYPE.at[name, "play_type"]],
    }

    for k, v in data.items():
        row[k] = aggregate_fn(v)

    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        default=1,
        # TODO: Need to decide on a proper hierarchy here. Higher values
        # are more granular.
        help="Specifies granularity level of hypergraph to build.",
    )
    parser.add_argument(
        "-t", "--use-type", action="store_true", help="If set, use type of play"
    )
    parser.add_argument("INPUT", nargs="+", type=str, help="Input filename(s)")

    args = parser.parse_args()

    rows = []

    for file in args.INPUT:
        df = pd.read_csv(file)
        hypergraphs = get_hypergraph(df, args.level)

        basename = get_filename_base(file)
        name = basename.split("_")[0]

        row = calculate_summary_statistics(name, hypergraphs)
        rows.append(pd.DataFrame.from_dict(row))

    df = pd.concat(rows)
    print(df)

    cols = [col for col in df.columns if col != "play"]

    df_melted = df.melt(id_vars=["play", "type"], var_name="variable")

    print(df_melted)

    # TODO include n in legend
    print(NAME_TO_TYPE.reset_index().groupby("play_type").count())

    sns.displot(
        df_melted,
        x="value",
        row="type" if args.use_type else None,
        hue="type" if args.use_type else None,
        col="variable",
        facet_kws={"sharex": False},
        common_bins=False,
    )

    plt.show()
