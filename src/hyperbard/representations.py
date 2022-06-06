from itertools import combinations
from typing import Union

import hypernetx as hnx
import networkx as nx
import pandas as pd

from hyperbard.utils import character_string_to_sorted_list, sort_join_strings


def get_weighted_multigraph(df: pd.DataFrame, groupby: list) -> nx.MultiGraph:
    """
    Create a weighted multigraph from an aggregated dataframe,
    with edges resolved at the level given by the groupby argument,
    where multiedges are kept, and n_tokens and n_lines are potential weights.

    Representations: ce-{scene, group}-{mb,mw}

    :param df: pd.DataFrame generated from an .agg.csv file
    :param groupby: ["act", "scene"] -> one edge per act and scene,
    ["act", "scene", "stagegroup"] -> one edge per act, scene, and stagegroup
    :return: nx.MultiGraph corresponding to the specified groupby
    """
    agg = dict(onstage=sort_join_strings, n_tokens=sum, n_lines=sum)
    df_aggregated = df.groupby(groupby).agg(agg).reset_index()
    df_aggregated["onstage"] = df_aggregated["onstage"].map(
        character_string_to_sorted_list
    )
    mG = nx.MultiGraph()
    for idx, row in df_aggregated.iterrows():
        mG.add_edges_from(
            list(combinations(row["onstage"], 2)),
            **{k: v for k, v in row.items() if k != "onstage"},
            edge_index=idx + 1,
        )
    return mG


def get_count_weighted_graph(df: pd.DataFrame, groupby: list):
    """
    Create a count-weighted graph from an aggregated dataframe,
    with edges resolved at the level given by the groupby argument,
    where multiedges are _not_ kept, and counts are potential weights.

    Representations: ce-{act,group}-{b,w}

    :param groupby: ["act", "scene"] -> one edge per act and scene, ["act", "scene", "stagegroup"] -> one edge per act, scene, and stagegroup
    :return: nx.Graph corresponding to the specified groupby
    """
    mG = get_weighted_multigraph(df, groupby)
    G = nx.Graph()
    for (u, v, k) in mG.edges(keys=True):
        if (u, v) in G.edges():
            G.edges[u, v]["count"] += 1
        else:
            G.add_edge(u, v, count=1)
    return G


def format_text_unit_node(elem):
    index_to_digits = {0: 1, 1: 2, 2: 4}
    return ".".join([str(e).zfill(index_to_digits[idx]) for idx, e in enumerate(elem)])


def get_bipartite_graph(
    df: pd.DataFrame, groupby: list
) -> Union[nx.Graph, nx.MultiDiGraph]:
    """
    Create a weighted bipartite graph from an aggregated dataframe,
    with play-part nodes resolved at the level given by the groupby argument,
    where n_tokens and n_lines are potential weights.

    Representations: se-{scene, group}-{b,w}, se-speech-mwd

    :param df: pd.DataFrame generated from an .agg.csv file
    :param groupby: ["act", "scene"] -> one play part node per act and scene, ["act", "scene", "stagegroup"] -> one play part node per act, scene, and stagegroup, ["act", "scene", "stagegroup", "setting", "speaker"] -> one play part node per act, scene, and stagegroup, directed edges for speech acts/information flow
    :return: nx.Graph (if groupby is not by speech act) or nx.MultiDiGraph (if groupby is by speech act)
    """
    agg = dict(onstage=sort_join_strings, n_tokens=sum, n_lines=sum)
    df_aggregated = df.groupby(groupby).agg(agg).reset_index()
    df_aggregated["onstage"] = df_aggregated["onstage"].map(
        character_string_to_sorted_list
    )
    text_units = [
        format_text_unit_node(elem)
        for elem in zip(
            *[df_aggregated[c].values for c in df_aggregated[groupby[:3]].columns]
        )
    ]
    if groupby == ["act", "scene", "stagegroup", "setting", "speaker"]:
        # TODO: lot's of modeling decisions here - document properly!
        # TODO se-speech-wd
        df_aggregated["speaker"] = df_aggregated["speaker"].map(
            character_string_to_sorted_list
        )
        G = nx.MultiDiGraph()
        G.add_nodes_from(text_units, node_type="text_unit")
        characters = [elem for sublist in df_aggregated.onstage for elem in sublist]
        G.add_nodes_from(characters, node_type="character")
        for idx, row in df_aggregated.iterrows():
            row_node = format_text_unit_node(tuple(row[x] for x in groupby[:3]))
            row_speaker_list = row["speaker"]
            row_lines = row["n_lines"]
            row_tokens = row["n_tokens"]
            for row_speaker in row_speaker_list:
                G.add_edge(
                    row_speaker, row_node, n_lines=row_lines, n_tokens=row_tokens
                )
            G.add_edges_from(
                [
                    (row_node, character)
                    for character in row["onstage"]
                    if character not in row_speaker_list
                ],
                n_lines=row_lines,
                n_tokens=row_tokens,
            )
    else:
        G = nx.Graph()
        G.add_nodes_from(
            [elem for sublist in df_aggregated.onstage for elem in sublist],
            node_type="character",
        )
        G.add_nodes_from(text_units, node_type="text_unit")
        for idx, row in df_aggregated.iterrows():
            row_node = format_text_unit_node(tuple(row[x] for x in groupby))
            G.add_edges_from(
                [(row_node, character) for character in row["onstage"]],
                n_lines=row["n_lines"],
                n_tokens=row["n_tokens"],
            )

    return G


def get_hypergraph(df: pd.DataFrame, groupby: list) -> hnx.Hypergraph:
    """
    Create an edge-weighted hypergraph from an aggregated dataframe,
    with edges resolved at the level given by the groupby argument,
    where multiedges are kept, and n_tokens and n_lines are potential weights.

    Representations: hg-{scene, group}-{mb,mw}

    :param groupby: ["act", "scene"] -> one edge per act and scene, ["act", "scene", "stagegroup"] -> one edge per act, scene, and stagegroup
    :return: hnx.HyperGraph corresponding to the specified groupby
    """
    # TODO edge-specific node weights
    # TODO hg-speech-{wd,mwd}
    df_grouped = (
        df.groupby(groupby)
        .agg({"n_tokens": "sum", "n_lines": "sum", "onstage": sort_join_strings})
        .reset_index()
    )
    df_grouped["onstage"] = df_grouped["onstage"].map(character_string_to_sorted_list)

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
