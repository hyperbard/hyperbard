"""Simple summary statistics for hypergraphs."""

import argparse
import collections

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from hypernetx.algorithms.s_centrality_measures import s_betweenness_centrality  
from hypernetx.algorithms.s_centrality_measures import s_closeness_centrality
from hypernetx.algorithms.s_centrality_measures import s_eccentricity

from hyperbard.utils import build_hypergraphs


def normalise(d):
    """Normalise dictionary values."""
    factor = sum(d.values())
    if factor > 0:
        return {k: v / factor for k, v in d.items()}
    else:
        return d


def calculate_ranking(hypergraphs):
    data = collections.defaultdict(list)
    eccentricity = collections.Counter()

    for k, v in hypergraphs.items():
        # TODO: go deeper/higher? I have not yet found a way to query
        # the hypergraph about its maximum $s$-connectivity.
        for s in [1, 2, 5]:
            values = normalise(s_closeness_centrality(v, s=s, edges=False))
            eccentricity.update(values)

            print(eccentricity)


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
    parser.add_argument("INPUT", type=str, help="Input filename")

    args = parser.parse_args()

    df = pd.read_csv(args.INPUT)
    hypergraphs = build_hypergraphs(df, args.level)
    calculate_ranking(hypergraphs)
