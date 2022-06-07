import pandas as pd
from utils import character_string_to_sorted_list, sort_join_strings, string_to_set


def get_hypergraph_edges(
    df: pd.DataFrame, groupby: list
) -> (pd.DataFrame, pd.DataFrame):
    """
    Create an edge-weighted hypergraph from an aggregated dataframe,
    with edges resolved at the level given by the groupby argument,
    where multiedges are kept, and n_tokens and n_lines are potential weights.

    Representations: hg-{scene, group}-{mb,mw}

    :param groupby: ["act", "scene"] -> one edge per act and scene, ["act", "scene", "stagegroup"] -> one edge per act, scene, and stagegroup
    :return: hnx.HyperGraph corresponding to the specified groupby
    """
    agg = {
        "n_tokens": "sum",
        "n_lines": "sum",
        "onstage": sort_join_strings,
    }
    df_grouped = df.groupby(groupby).agg(agg).reset_index()
    df_grouped["onstage"] = df_grouped["onstage"].map(character_string_to_sorted_list)
    # for node weights <- lines of speech
    df_speaker_exploded = df.copy()
    df_speaker_exploded.speaker = df_speaker_exploded.speaker.map(string_to_set)
    df_speaker_exploded = df_speaker_exploded.explode("speaker")
    speaker_groupby = groupby + ["speaker"] if "speaker" not in groupby else groupby
    speaker_weights = (
        df_speaker_exploded.groupby(speaker_groupby)
        .agg({"n_tokens": "sum", "n_lines": "sum"})
        .reset_index()
        .rename(
            dict(
                speaker="node", n_lines="n_lines_speaker", n_tokens="n_tokens_speaker"
            ),
            axis=1,
        )
    )
    # for node weights <- lines onstage
    df_onstage_exploded = df.copy()
    df_onstage_exploded.onstage = df_onstage_exploded.onstage.map(string_to_set)
    df_onstage_exploded = df_onstage_exploded.explode("onstage")
    onstage_weights = (
        df_onstage_exploded.groupby(groupby + ["onstage"])
        .agg({"n_tokens": "sum", "n_lines": "sum"})
        .reset_index()
        .rename(
            dict(
                onstage="node", n_lines="n_lines_onstage", n_tokens="n_tokens_onstage"
            ),
            axis=1,
        )
    )
    merge_columns = ["node"] + groupby
    edge_specific_node_weights = speaker_weights.merge(
        onstage_weights, left_on=merge_columns, right_on=merge_columns, how="outer"
    ).fillna(0)
    edge_specific_node_weights.n_lines_speaker = (
        edge_specific_node_weights.n_lines_speaker.astype(int)
    )
    edge_specific_node_weights.n_tokens_speaker = (
        edge_specific_node_weights.n_tokens_speaker.astype(int)
    )
    edge_specific_node_weights.n_lines_onstage = (
        edge_specific_node_weights.n_lines_onstage.astype(int)
    )
    edge_specific_node_weights.n_tokens_onstage = (
        edge_specific_node_weights.n_tokens_onstage.astype(int)
    )

    df_grouped.onstage = df_grouped.onstage.map(sort_join_strings)
    return df_grouped, edge_specific_node_weights
    # H = hnx.Hypergraph()
    # for idx, row in df_grouped.iterrows():
    #     H.add_edge(
    #         hnx.Entity(
    #             idx,
    #             row["onstage"],
    #             **{k: v for k, v in row.items() if k != "onstage"},
    #         )
    #     )
    # return H


def get_multi_directed_hypergraph_edges(df: pd.DataFrame) -> pd.DataFrame:
    """

    Representation: hg-speech-mwd

    :param df:
    :return:
    """
    groupby = ["act", "scene", "stagegroup", "setting", "speaker"]
    agg = {
        "n_tokens": "sum",
        "n_lines": "sum",
        "onstage": sort_join_strings,
    }
    df_grouped = df.groupby(groupby).agg(agg).reset_index()
    df_grouped["onstage"] = df_grouped["onstage"].map(character_string_to_sorted_list)
    df_grouped["speaker"] = df_grouped["speaker"].map(character_string_to_sorted_list)
    df_grouped.onstage = df_grouped.onstage.map(sort_join_strings)
    df_grouped.speaker = df_grouped.speaker.map(sort_join_strings)
    column_order = [
        "act",
        "scene",
        "stagegroup",
        "setting",
        "speaker",
        "onstage",
        "n_tokens",
        "n_lines",
    ]
    return df_grouped[column_order]


def get_weighted_directed_hypergraph_edges(df: pd.DataFrame) -> pd.DataFrame:
    df_mwd = get_multi_directed_hypergraph_edges(df)
    df_mwd = (
        df_mwd.groupby(["act", "scene", "stagegroup", "speaker", "onstage"])
        .agg(dict(n_tokens=sum, n_lines=sum))
        .reset_index()
    )
    return df_mwd


def get_hypergraph_nodes(df: pd.DataFrame) -> pd.DataFrame:
    df_exploded_onstage = df.copy()
    df_exploded_onstage.onstage = df_exploded_onstage.onstage.map(string_to_set)
    df_exploded_onstage = df_exploded_onstage.explode("onstage")
    nodes = pd.DataFrame()
    nodes["node"] = sorted(df_exploded_onstage.onstage.unique())
    nodes["n_lines_onstage"] = nodes.node.map(
        lambda node: df_exploded_onstage.query("onstage == @node").n_lines.sum()
    )
    nodes["n_tokens_onstage"] = nodes.node.map(
        lambda node: df_exploded_onstage.query("onstage == @node").n_tokens.sum()
    )
    df_exploded_speaker = df.copy()
    df_exploded_speaker.speaker = df_exploded_speaker.speaker.map(string_to_set)
    df_exploded_speaker = df_exploded_speaker.explode("speaker")
    nodes["n_lines_speaker"] = nodes.node.map(
        lambda node: df_exploded_speaker.query("speaker == @node").n_lines.sum()
    )
    nodes["n_tokens_speaker"] = nodes.node.map(
        lambda node: df_exploded_speaker.query("speaker == @node").n_tokens.sum()
    )
    return nodes[
        [
            "node",
            "n_lines_onstage",
            "n_lines_speaker",
            "n_tokens_onstage",
            "n_tokens_speaker",
        ]
    ]
