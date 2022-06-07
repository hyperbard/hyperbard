"""Simple summary statistics for hypergraphs."""

from collections import OrderedDict, defaultdict

import hypernetx as hnx
import networkx as nx
import numpy as np
import pandas as pd

from hyperbard.graph_representations import (
    get_bipartite_graph,
    get_count_weighted_graph,
    get_weighted_multigraph,
)

from hyperbard.hypergraph_representations import (
    get_hypergraph_edges,
    get_hypergraph_nodes,
    get_multi_directed_hypergraph_edges,
    get_weighted_directed_hypergraph_edges,
)


def s_degree_centrality(H, s=1, weight=None):
    """Calculate degree centrality values of a hypergraph."""
    values = {}
    for node in H.nodes:
        values[node] = H.degree(node, s=s)

        if weight is not None:
            # Get all edges of size at least `s` in which the specific
            # node participates.
            memberships = H.nodes[node].memberships
            edges = set(e for e in memberships if len(H.edges[e]) >= s)

            # Just to be sure this does not come back and bite us...
            assert len(edges) == values[node]

            values[node] = sum(getattr(H.edges[e], weight) for e in edges)

    return values


def degree_centrality(G, weight=None, centrality=None):
    """Wrapper function for degree centrality of (hyper)graphs."""
    if isinstance(G, hnx.Hypergraph):
        return degree_centrality_hypergraph(G, weight=weight, centrality=centrality)
    else:
        return degree_centrality_graph(G, weight=weight, centrality=centrality)


def degree_centrality_graph(G, weight=None, centrality=None):
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


def s_degree(H, s=1, weight=None, superlevel=True):
    """Calculate degree  values of a hypergraph.

    This function calculates the (weighted) degree of a hypergraph,
    focusing either on edges of cardinality at least `s` or at most
    `s` (in case `superlevel == False`).

    Parameters
    ----------
    H : hnx.Hypergraph
        Hypergraph

    s : int
        Specifies connectivity threshold. The flag `superlevel` controls
        the direction of said threshold.

    weight : str or `None`
        If set, queries the specific edge attribute to use as a weight
        for the degree calculation.

    superlevel : bool
        If set, `s` is treated as a *minimum* connectivity threshold. If
        not set, `s` is treated as a maximum.

    Returns
    -------
    dict
        Dictionary with nodes as keys and values as (weighted) degrees.
    """
    values = {}
    for node in H.nodes:
        if weight is not None:
            # Get all edges of size at least `s` (if `superlevel` is
            # set) in which the specific node participates.
            memberships = H.nodes[node].memberships
            if superlevel:
                edges = set(e for e in memberships if len(H.edges[e]) >= s)
            else:
                edges = set(e for e in memberships if len(H.edges[e]) <= s)

            values[node] = sum(getattr(H.edges[e], weight) for e in edges)

    return values


def degree_hypergraph(H, weight=None, centrality=None):
    values = s_degree(H, s=1, weight=weight)
    return values


# TODO: Ignoring most of the input parameters at the moment.
def degree_centrality_hypergraph(H, weight=None, centrality=None):
    # Auxiliary function for normalising a dictionary (or really any
    # other type of key--value store).
    def _normalise(d):
        factor = sum(d.values())
        if factor > 0:
            return {k: v / factor for k, v in d.items()}
        else:
            return d

    # TODO: Make configurable?
    normalise = True

    # Store centrality values for each node. Since we are iterating over
    # different `s` connectivity values, multiple centrality values will
    # be stored and have to be aggregated later.
    centrality = defaultdict(list)

    # TODO: Make configurable? I have not yet found a way to query the
    # hypergraph about its maximum $s$-connectivity.
    for s in [1, 2, 5]:
        values = s_degree_centrality(H, s=s, weight=weight)

        if normalise:
            values = _normalise(values)

        for k, v in values.items():
            centrality[k].append(v)

    # TODO: Make configurable
    agg_fn = np.sum

    centrality = {k: agg_fn(v) for k, v in centrality.items()}

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
    G = get_count_weighted_graph(df, groupby=["act", "scene"])
    G2 = get_count_weighted_graph(df, groupby=["act", "scene", "stagegroup"])
    mG = get_weighted_multigraph(df, groupby=["act", "scene"])
    mG2 = get_weighted_multigraph(df, groupby=["act", "scene", "stagegroup"])
    bG = get_bipartite_graph(df, groupby=["act", "scene"])
    bG2 = get_bipartite_graph(df, groupby=["act", "scene", "stagegroup"])
    bG3 = get_bipartite_graph(
        df, groupby=["act", "scene", "stagegroup", "setting", "speaker"]
    )
    hG1 = get_hypergraph(df, groupby=["act", "scene"])
    hG2 = get_hypergraph(df, groupby=["act", "scene", "stagegroup"])
    ranks = OrderedDict(
        {
            "01_se-scene-b": character_rank_dictionary(
                centrality_ranking_with_equalities(bG)
            ),
            "02_se-scene-w": character_rank_dictionary(
                centrality_ranking_with_equalities(bG, weight="n_lines")
            ),
            "03_se-group-b": character_rank_dictionary(
                centrality_ranking_with_equalities(bG2)
            ),
            "04_se-group-w": character_rank_dictionary(
                centrality_ranking_with_equalities(bG2, weight="n_lines")
            ),
            "05_se-speech-wd_in": character_rank_dictionary(
                centrality_ranking_with_equalities(
                    bG3, weight="n_lines", centrality="in"
                )
            ),
            "06_se-speech-wd_out": character_rank_dictionary(
                centrality_ranking_with_equalities(
                    bG3, weight="n_lines", centrality="out"
                )
            ),
            "07_ce-scene-b": character_rank_dictionary(
                centrality_ranking_with_equalities(G)
            ),
            "08_ce-scene-mb": character_rank_dictionary(
                centrality_ranking_with_equalities(mG)
            ),
            "09_ce-scene-mw": character_rank_dictionary(
                centrality_ranking_with_equalities(mG, weight="n_lines")
            ),
            "10_ce-group-b": character_rank_dictionary(
                centrality_ranking_with_equalities(G2)
            ),
            "11_ce-group-mb": character_rank_dictionary(
                centrality_ranking_with_equalities(mG2)
            ),
            "12_act_group-mw": character_rank_dictionary(
                centrality_ranking_with_equalities(mG2, weight="n_lines")
            ),
            "13_hg-scene-mb": character_rank_dictionary(
                centrality_ranking_with_equalities(hG1)
            ),
            "14_hg-scene-mw": character_rank_dictionary(
                centrality_ranking_with_equalities(hG1, weight="n_lines")
            ),
            "15_hg-group-mb": character_rank_dictionary(
                centrality_ranking_with_equalities(hG2)
            ),
            "16_hg-group-mw": character_rank_dictionary(
                centrality_ranking_with_equalities(hG2, weight="n_lines")
            ),
        }
    )
    rank_df = pd.DataFrame.from_records(ranks).reset_index()
    return rank_df.sort_values(by=rank_df.columns[-1])
