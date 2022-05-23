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


def calculate_centrality(hypergraphs, normalise=True):
    """Calculate centrality for all nodes.

    This function accumulates all centrality values over different
    s-connectivity thresholds and stores them for each node.

    Parameters
    ----------
    normalise : bool
        If set, normalise centralities to sum to one, thus counting the
        overall contributions to centrality for each node.

    Returns
    -------
    pd.DataFrame
        Data frame containing node names (i.e. characters) as its index,
        and different centrality measures as columns.
    """
    # Key will be the name of a centrality measure; the value will be
    # the standard counter
    centrality = collections.defaultdict(collections.Counter)

    # Auxiliary function for normalising a dictionary (or really any
    # other type of key--value store).
    def _normalise(d):
        factor = sum(d.values())
        if factor > 0:
            return {k: v / factor for k, v in d.items()}
        else:
            return d

    centrality_functions = {
        'betweenness_centrality': s_betweenness_centrality,
        'closeness_centrality': s_closeness_centrality,
        'eccentricity': s_eccentricity,
    }

    for k, v in hypergraphs.items():
        # TODO: go deeper/higher? I have not yet found a way to query
        # the hypergraph about its maximum $s$-connectivity.
        for s in [1, 2, 5]:
            for name, fn in centrality_functions.items():
                values = fn(v, s=s, edges=False)

                if normalise:
                    values = _normalise(values)

                centrality[name].update(values)

    columns = [
        pd.Series(values, name=name).sort_index()
        for name, values in centrality.items()
    ]

    df = pd.concat(columns, axis='columns')
    df.index.name = 'character'
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT", type=str, help="Input filename")

    args = parser.parse_args()

    df_data = pd.read_csv(args.INPUT)

    # TODO: Go over all levels...
    hypergraphs = build_hypergraphs(df_data, 1)
    df = calculate_centrality(hypergraphs)

    df_ranked = df.rank(axis='rows', method='min', ascending=False)
    g = sns.lineplot(data=df_ranked.T, legend=False)

    labels = df_ranked[df_ranked.columns[0]].sort_values()
    g.set_yticks(labels.values)
    g.set_yticklabels(labels.index.values)

    plt.show()
