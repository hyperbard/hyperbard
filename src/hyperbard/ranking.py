"""Simple summary statistics for hypergraphs."""

import collections

import hypernetx as hnx
import networkx as nx
import numpy as np
import pandas as pd


from hyperbard.representations import (
    get_bipartite_graph,
    get_count_weighted_graph,
    get_hypergraph,
    get_weighted_multigraph,
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

            values[node] = sum(
                getattr(H.edges[e], weight) for e in edges
            )

    return values


def degree_centrality(G, weight=None, centrality=None):
    """Wrapper function for degree centrality of (hyper)graphs."""
    if isinstance(G, hnx.Hypergraph):
        return degree_centrality_hypergraph(
            G,
            weight=weight,
            centrality=centrality
        )
    else:
        return degree_centrality_graph(
            G,
            weight=weight,
            centrality=centrality
        )


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
    centrality = collections.defaultdict(list)

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

    centrality = {
        k: agg_fn(v) for k, v in centrality.items()
    }

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
    hG1 = get_hypergraph(df, groupby=["act", "scene"])
    hG2 = get_hypergraph(df, groupby=["act", "scene", "stagegroup"])
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
        "07_hypergraph_act_scene": character_rank_dictionary(
            centrality_ranking_with_equalities(hG1)
        ),
        "08_hypergraph_act_scene_lines": character_rank_dictionary(
            centrality_ranking_with_equalities(hG1, weight="n_lines")
        ),
        "08_hypergraph_act_scene_stagegroup": character_rank_dictionary(
            centrality_ranking_with_equalities(hG2)
        ),
        "09_hypergraph_act_scene_stagegroup_lines": character_rank_dictionary(
            centrality_ranking_with_equalities(hG2, weight="n_lines")
        ),
    }
    rank_df = pd.DataFrame.from_records(ranks).reset_index()
    return rank_df.sort_values(by=rank_df.columns[-1])
