"""Ranking for (hyper)graphs.

Notice that while other metrics, such as different centrality measures,
would be possible, we are focusing on *degree* statistics for now since
they are readily interpretable for both graphs and hypergraphs.
"""

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


# TODO: WIP
def from_edges(df_grouped):
    H = hnx.Hypergraph()
    for idx, row in df_grouped.iterrows():
        H.add_edge(
            hnx.Entity(
                idx,
                row["onstage"],
                **{k: v for k, v in row.items() if k != "onstage"},
            )
        )
    return H


def s_degree(H, s=1, weight=None, superlevel=True):
    """Calculate degree values of a hypergraph.

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


def calculate_degree(G, weight=None, degree_type=None):
    """Calculate degree values of a graph.

    This is essentially a wrapper function around `nx.degree` that is
    capable of accounting for weights.

    Parameters
    ----------
    degree: None or "in" or "out"

    weight : None or str
        If specified, access edge attribute named `weight` to calculate
        weighted degrees.

    Returns
    -------
    dict
        Dictionary with nodes as key and (weighted) degrees as values.
    """
    # Defenses against garbage input
    if degree_type not in [None, "in", "out"]:
        raise ValueError(
            f"degree_type={degree_type}, must be in {[None, 'in', 'out']}!"
        )
    if degree_type is not None and type(G) not in [nx.DiGraph, nx.MultiDiGraph]:
        raise ValueError(
            f"type(G)={type(G)}, must be in {[nx.DiGraph, nx.MultiDiGraph]} because degree={degree}!"
        )
    # Actual degree computation
    if weight is not None:
        assert (
            weight in list(G.edges(data=True))[0][-1].keys()
        ), f"Attribute '{weight}'\
            is not an edge attribute! Edge attributes are: {list(list(G.edges(data=True))[0][-1].keys())}"
    if "node_type" not in list(dict(G.nodes(data=True)).values())[0].keys():
        if weight is None:
            degrees = dict(nx.degree(G))
        else:
            degrees = dict(nx.degree(G, weight=weight))
    else:
        character_nodes = [
            n for n, node_type in G.nodes(data="node_type") if node_type == "character"
        ]
        if type(G) == nx.Graph:
            degrees = dict(G.degree(character_nodes, weight=weight))
        # TODO: Check whether `DiGraphs` are supported correctly
        elif type(G) in [nx.DiGraph, nx.MultiDiGraph]:
            if degree_type == "out":
                degree_func = G.out_degree
            elif degree_type == "in":
                degree_func = G.in_degree
            else:
                degree_func = G.degree
            degrees = dict(degree_func(character_nodes, weight=weight))
        else:
            raise NotImplementedError(f"Unexpected graph type: {type(G)}!")

    return degrees


def degree_wrapper(G, weight=None, degree_type=None):
    """Wrapper function for degree calculation of (hyper)graphs."""
    if isinstance(G, hnx.Hypergraph):
        # TODO: Incorporate `degree_type` variable.
        return s_degree(G, s=1, weight=weight)
    else:
        return calculate_degree(G, weight=weight, degree_type=degree_type)


def degree_ranking(G, weight=None, degree_type=None):
    """
    degree: None or "in" or "out"
    """
    return sorted(
        degree_wrapper(G, weight, degree_type).items(),
        key=lambda tup: tup[-1],
        reverse=True,
    )


def degree_ranking_with_equalities(G, weight=None, degree_type=None):
    """
    degree: None or "in" or "out"
    output: list of tuples [({set of characters}, degree), ...], sorted by degree descending
    """
    ranking_list = degree_ranking(G, weight, degree_type)
    new_list = []
    for character, degree in ranking_list:
        if new_list and degree == new_list[-1][-1]:
            new_list[-1][0].add(character)
        else:
            new_list.append(({character}, degree))

    return new_list


def character_rank_dictionary(ranking):
    rank_dict = dict()
    rank = 1
    for (characters, _) in ranking:
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

    # TODO: Does *not* yet use the right weights.
    hg_scene_mw = from_edges(get_hypergraph_edges(df, groupby=["act", "scene"])[0])
    hg_group_mw = from_edges(
        get_hypergraph_edges(df, groupby=["act", "scene", "stagegroup"])[0]
    )
    hg_speech_mwd = from_edges(get_multi_directed_hypergraph_edges(df))
    hg_speech_wd = from_edges(get_weighted_directed_hypergraph_edges(df))

    ranks = OrderedDict(
        {
            "01_se-scene-b": character_rank_dictionary(
                degree_ranking_with_equalities(bG)
            ),
            "02_se-scene-w": character_rank_dictionary(
                degree_ranking_with_equalities(bG, weight="n_lines")
            ),
            "03_se-group-b": character_rank_dictionary(
                degree_ranking_with_equalities(bG2)
            ),
            "04_se-group-w": character_rank_dictionary(
                degree_ranking_with_equalities(bG2, weight="n_lines")
            ),
            "05_se-speech-wd_in": character_rank_dictionary(
                degree_ranking_with_equalities(bG3, weight="n_lines", degree_type="in")
            ),
            "06_se-speech-wd_out": character_rank_dictionary(
                degree_ranking_with_equalities(bG3, weight="n_lines", degree_type="out")
            ),
            "07_ce-scene-b": character_rank_dictionary(
                degree_ranking_with_equalities(G)
            ),
            "08_ce-scene-mb": character_rank_dictionary(
                degree_ranking_with_equalities(mG)
            ),
            "09_ce-scene-mw": character_rank_dictionary(
                degree_ranking_with_equalities(mG, weight="n_lines")
            ),
            "10_ce-group-b": character_rank_dictionary(
                degree_ranking_with_equalities(G2)
            ),
            "11_ce-group-mb": character_rank_dictionary(
                degree_ranking_with_equalities(mG2)
            ),
            "12_act_group-mw": character_rank_dictionary(
                degree_ranking_with_equalities(mG2, weight="n_lines")
            ),
            # "13_hg-scene-mb": character_rank_dictionary(
            #    degree_ranking_with_equalities(hg_scene_mw)
            # ),
            # "14_hg-scene-mw": character_rank_dictionary(
            #    degree_ranking_with_equalities(hg_scene_mw, weight="n_lines")
            # ),
            # "15_hg-group-mb": character_rank_dictionary(
            #    degree_ranking_with_equalities(hg_group_mw)
            # ),
            # "16_hg-group-mw": character_rank_dictionary(
            #    degree_ranking_with_equalities(hg_group_mw, weight="n_lines")
            # ),
        }
    )
    rank_df = pd.DataFrame.from_records(ranks).reset_index()
    return rank_df.sort_values(by=rank_df.columns[-1])


def get_character_ranking(representations):
    ranks = OrderedDict()

    for representation in representations:
        name = representation["name"]
        graph = representation["graph"]
        weight = representation.get("weight", None)
        degree = representation.get("degree", None)

        ranks[name] = character_rank_dictionary(
            degree_ranking_with_equalities(graph, weight=weight, degree_type=degree)
        )

    rank_df = (
        pd.DataFrame.from_records(ranks)
        .rename(
            # Rename columns by dropping the 'XX-' prefix.
            mapper=lambda x: "-".join(x.split("-")[1:]),
            axis="columns",
        )
        .reset_index()
    )

    return rank_df.sort_values(by=rank_df.columns[-1])
