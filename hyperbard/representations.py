from itertools import combinations

import hypernetx as hnx
import networkx as nx
import pandas as pd

from hyperbard.utils import character_string_to_sorted_list, sort_join_strings


def get_weighted_multigraph(df: pd.DataFrame, groupby: list):
    """
    groupby = ["act", "scene"] -> one edge per act and scene
    groupby = ["act", "scene", "stagegroup"] -> one edge per act, scene, and stagegroup
    multi-edges are kept, with n_tokens or n_lines as potential weights
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
            scene_index=idx,
        )
    return mG


def get_bipartite_graph(df: pd.DataFrame, groupby: list):
    """
    groupby = ["act", "scene"] -> one play part node per act and scene
    groupby = ["act", "scene", "stagegroup"] -> one play part node per act, scene, and stagegroup
    groupby = ["act", "scene", "stagegroup", "setting", "speaker"] ->
    n_tokens or n_lines are potential weights
    """
    agg = dict(onstage=sort_join_strings, n_tokens=sum, n_lines=sum)
    df_aggregated = df.groupby(groupby).agg(agg).reset_index()
    df_aggregated["onstage"] = df_aggregated["onstage"].map(
        character_string_to_sorted_list
    )
    if groupby == ["act", "scene", "stagegroup", "setting", "speaker"]:
        # TODO: lot's of modeling decisions here - document properly!
        df_aggregated["speaker"] = df_aggregated["speaker"].map(
            character_string_to_sorted_list
        )
        G = nx.MultiDiGraph()
        text_units = list(
            zip(*[df_aggregated[c].values for c in df_aggregated[groupby[:3]].columns])
        )
        G.add_nodes_from(
            [elem for sublist in df_aggregated.onstage for elem in sublist],
            node_type="character",
        )
        G.add_nodes_from(text_units, node_type="text_unit")
        for idx, row in df_aggregated.iterrows():
            row_node = tuple(row[x] for x in groupby[:3])
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
        text_units = list(
            zip(*[df_aggregated[c].values for c in df_aggregated[groupby].columns])
        )
        G.add_nodes_from(
            [elem for sublist in df_aggregated.onstage for elem in sublist],
            node_type="character",
        )
        G.add_nodes_from(text_units, node_type="text_unit")
        for idx, row in df_aggregated.iterrows():
            row_node = tuple(row[x] for x in groupby)
            G.add_edges_from(
                [(row_node, character) for character in row["onstage"]],
                n_lines=row["n_lines"],
                n_tokens=row["n_tokens"],
            )

    return G


def get_count_weighted_graph(df: pd.DataFrame, groupby: list):
    """
    groupby = ["act", "scene"] -> one edge per act and scene
    groupby = ["act", "scene", "stagegroup"] -> one edge per act, scene, and stagegroup
    multi-edges are transformed into counts, which can serve as weights
    """
    mG = get_weighted_multigraph(df, groupby)
    G = nx.Graph()
    for (u, v, k) in mG.edges(keys=True):
        if (u, v) in G.edges():
            G.edges[u, v]["count"] += 1
        else:
            G.add_edge(u, v, count=1)
    return G


def get_hypergraph(df: pd.DataFrame, groupby: list):
    """
    groupby = ["act", "scene"] -> one edge per act and scene
    groupby = ["act", "scene", "stagegroup"] -> one edge per act, scene, and stagegroup
    """
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
