"""Simple summary statistics for hypergraphs."""

import argparse
import collections

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns
from hypernetx.algorithms.s_centrality_measures import (
    s_betweenness_centrality,
    s_closeness_centrality,
    s_eccentricity,
    s_harmonic_centrality,
)

from hyperbard.representations import (
    get_bipartite_graph,
    get_count_weighted_graph,
    get_hypergraphs,
    get_weighted_multigraph,
)


def s_degree_centrality(H, s=1, **kwargs):
    """Calculate degree centrality values of a hypergraph."""
    values = {}
    for node in H.nodes:
        values[node] = H.s_degree(node, s=s)
    return values


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
        "betweenness_centrality": s_betweenness_centrality,
        "closeness_centrality": s_closeness_centrality,
        "degree_centrality": s_degree_centrality,
        "eccentricity": s_eccentricity,
        "harmonic_centrality": s_harmonic_centrality,
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
        pd.Series(values, name=name).sort_index() for name, values in centrality.items()
    ]

    df = pd.concat(columns, axis="columns")
    df.index.name = "character"
    return df


def degree_centrality(G, weight=None, centrality=None):
    """
    centrality: None or "in" or "out"
    Wrapper around nx.degree_centrality that allows to account for weights.
    When weight attribute is specified, returns fraction of degree sum in which node participates.
    """
    # Defenses against garbage input
    if centrality not in [None, "in", "out"]:
        raise ValueError(f"centrality={centrality}, must be in {[None, 'in', 'out']}!")
    if centrality is not None and type(G) not in [nx.DiGraph, nx.MultiDiGraph]:
        raise ValueError(
            f"type(G)={type(G)}, must be in {[nx.DiGraph, nx.MultiDiGraph]} because centrality={centrality}!"
        )
    # Actual centrality computation
    if weight is not None:
        assert (
            weight in list(G.edges(data=True))[0][-1].keys()
        ), f"Attribute '{weight}'\
            is not an edge attribute! Edge attributes are: {list(list(G.edges(data=True))[0][-1].keys())}"
    if "node_type" not in list(dict(G.nodes(data=True)).values())[0].keys():
        if weight is None:
            centrality = nx.degree_centrality(G)
        else:
            s = 1.0 / sum(dict(G.degree(weight=weight)).values())
            centrality = {n: d * s for n, d in G.degree(weight=weight)}
    else:
        character_nodes = [
            n for n, node_type in G.nodes(data="node_type") if node_type == "character"
        ]
        if type(G) == nx.Graph:
            s = 1.0 / sum(dict(G.degree(character_nodes, weight=weight)).values())
            centrality = {n: d * s for n, d in G.degree(character_nodes, weight=weight)}
        elif type(G) == nx.MultiDiGraph:
            if centrality == "out":
                degree_func = G.out_degree
            elif centrality == "in":
                degree_func = G.in_degree
            else:
                degree_func = G.degree
            s = 1.0 / sum(dict(degree_func(character_nodes, weight=weight)).values())
            centrality = {
                n: d * s for n, d in degree_func(character_nodes, weight=weight)
            }
        else:
            raise NotImplementedError(f"Unexpected graph type: {type(G)}!")
    return centrality


def centrality_ranking(G, weight=None, centrality=None):
    """
    centrality: None or "in" or "out"
    """
    return sorted(
        degree_centrality(G, weight, centrality).items(),
        key=lambda tup: tup[-1],
        reverse=True,
    )


def centrality_ranking_with_equalities(G, weight=None, centrality=None):
    """
    centrality: None or "in" or "out"
    output: list of tuples [({set of characters}, centrality), ...], sorted by centrality descending
    """
    ranking_list = centrality_ranking(G, weight, centrality)
    new_list = []
    for character, centrality in ranking_list:
        if new_list and centrality == new_list[-1][-1]:
            new_list[-1][0].add(character)
        else:
            new_list.append(({character}, centrality))
    return new_list


def character_rank_dictionary(centrality_ranking):
    rank_dict = dict()
    rank = 1
    for (characters, _) in centrality_ranking:
        for character in characters:
            rank_dict[character] = rank
        rank += len(characters)
    return rank_dict


def get_character_ranking_df(df):
    mG = get_weighted_multigraph(df, groupby=["act", "scene"])
    mG2 = get_weighted_multigraph(df, groupby=["act", "scene", "stagegroup"])
    G = get_count_weighted_graph(df, groupby=["act", "scene"])
    G2 = get_count_weighted_graph(df, groupby=["act", "scene", "stagegroup"])
    bG = get_bipartite_graph(df, groupby=["act", "scene"])
    bG2 = get_bipartite_graph(df, groupby=["act", "scene", "stagegroup"])
    bG3 = get_bipartite_graph(
        df, groupby=["act", "scene", "stagegroup", "setting", "speaker"]
    )
    ranks = {
        "001_act_scene_bipartite": character_rank_dictionary(
            centrality_ranking_with_equalities(bG)
        ),
        "002_act_scene_bipartite_lines": character_rank_dictionary(
            centrality_ranking_with_equalities(bG, weight="n_lines")
        ),
        "003_act_scene_stagegroup_bipartite": character_rank_dictionary(
            centrality_ranking_with_equalities(bG2)
        ),
        "004_act_scene_stagegroup_bipartite_lines": character_rank_dictionary(
            centrality_ranking_with_equalities(bG2, weight="n_lines")
        ),
        "005_act_scene_stagegroup_setting_bipartite_lines_in": character_rank_dictionary(
            centrality_ranking_with_equalities(bG3, weight="n_lines", centrality="in")
        ),
        "006_act_scene_stagegroup_setting_bipartite_lines_out": character_rank_dictionary(
            centrality_ranking_with_equalities(bG3, weight="n_lines", centrality="out")
        ),
        "01_act_scene_simple": character_rank_dictionary(
            centrality_ranking_with_equalities(G)
        ),
        "02_act_scene_multi": character_rank_dictionary(
            centrality_ranking_with_equalities(mG)
        ),
        "03_act_scene_multi_lines": character_rank_dictionary(
            centrality_ranking_with_equalities(mG, weight="n_lines")
        ),
        "04_act_scene_stagegroup_simple": character_rank_dictionary(
            centrality_ranking_with_equalities(G2)
        ),
        "05_act_scene_stagegroup_multi": character_rank_dictionary(
            centrality_ranking_with_equalities(mG2)
        ),
        "06_act_scene_stagegroup_multi_lines": character_rank_dictionary(
            centrality_ranking_with_equalities(mG2, weight="n_lines")
        ),
    }
    rank_df = pd.DataFrame.from_records(ranks).reset_index()
    return rank_df.sort_values(by=rank_df.columns[-1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT", type=str, help="Input filename")

    args = parser.parse_args()

    df_data = pd.read_csv(args.INPUT)

    # Store rankings over different representations. They key describes
    # the representation, the value contains the ranked data frame.
    rankings = {}

    # TODO: Refactor to account for different representations
    for level in [1, 2]:
        hypergraphs = get_hypergraphs(df_data, level=level)
        df = calculate_centrality(hypergraphs)

        df_ranked = df.rank(axis="rows", method="min")
        rankings[f"level{level}"] = df_ranked

    fig, ax = plt.subplots(nrows=len(rankings))

    for axis, rep in zip(ax.ravel(), rankings.keys()):
        axis.set_title(rep)
        df = rankings[rep]
        g = sns.lineplot(data=df.T, legend=False, ax=axis)

        labels = df[df.columns[0]].sort_values()
        g.set_yticks(labels.values)
        g.set_yticklabels(labels.index.values)

    plt.show()
