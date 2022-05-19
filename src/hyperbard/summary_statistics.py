"""Simple summary statistics for hypergraphs."""

import argparse
import collections

import hypernetx as hnx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from hyperbard.preprocessing import get_filename_base
from hyperbard.statics import META_PATH

NAME_TO_TYPE = pd.read_csv(f"{META_PATH}/playtypes.csv").set_index("play_name")


def build_hypergraphs(df, level):
    """Build hypergraphs of specified level and return them."""
    if level == 1:
        edges = []
        for (act, scene), group in (
            df.groupby(["act", "scene", "onstage"])
            .agg(dict(n_tokens="sum"))
            .reset_index()
            .groupby(["act", "scene"])
        ):
            joined_group = tuple(sorted(set(" ".join(group.onstage).split())))
            edges.append(joined_group)

        H = hnx.Hypergraph(edges)
        return {"full": H}

    elif level == 2:
        df_grouped = (
            df.groupby(["stagegroup", "onstage", "act", "scene"])
            .agg({"n_tokens": "sum"})
            .reset_index()
        )
        df_grouped.onstage = df_grouped.onstage.map(lambda x: tuple(x.split()))

        Hs = {
            (act, scene): hnx.Hypergraph(
                dict(df_grouped.query("act == @act and scene == @scene").onstage)
            )
            for (act, scene) in set(zip(df.act, df.scene))
        }

        return Hs


def calculate_summary_statistics(name, hypergraphs, aggregate_fn=np.mean):
    """Given a set of hypergraphs, calculate summary statistics.

    This function will create a single row of a larger data frame,
    ultimately comprising more than one set of stats for one play.
    """
    data = collections.defaultdict(list)

    for k, v in hypergraphs.items():
        # TODO: go deeper/higher?
        for s in [1]:
            comp = list(v.s_components(s))
            data[f"{s}_connected_components"].append(len(comp))

            if v.is_connected(s):
                diam = v.diameter(s)
                data[f"{s}_diameter"].append(diam)

            # TODO: not sure if this is the right way.
            node_diameters = v.node_diameters(s)
            data[f"avg_node_{s}_diameter"].append(np.mean(node_diameters[s]))

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
        "-t", "--use-type", action="store_true", help="If set use type of play"
    )
    parser.add_argument("INPUT", nargs="+", type=str, help="Input filename(s)")

    args = parser.parse_args()

    rows = []

    for file in args.INPUT:
        df = pd.read_csv(file)
        hypergraphs = build_hypergraphs(df, args.level)

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
