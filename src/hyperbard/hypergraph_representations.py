import pandas as pd
from utils import character_string_to_sorted_list, sort_join_strings, string_to_set


def _explode_df(df, explode_column):
    """

    :param df:
    :param explode_column:
    :return:
    """
    df_exploded = df.copy()
    df_exploded[explode_column] = df_exploded[explode_column].map(string_to_set)
    return df_exploded.explode(explode_column)


def get_hypergraph_edges(
    df: pd.DataFrame, groupby: list
) -> (pd.DataFrame, pd.DataFrame):
    """
    Create an edge-weighted hypergraph from an aggregated dataframe,
    with edges resolved at the level given by the groupby argument,
    where multiedges are kept, and n_tokens and n_lines are potential weights.

    Representations: hg-{scene, group}-{mb,mw}

    :param groupby: ["act", "scene"] -> one edge per act and scene, ["act", "scene", "stagegroup"] -> one edge per act, scene, and stagegroup
    :return: tuple of pd.DataFrame objects corresponding to (edges, edge_specific_node_weights)
    """
    agg = {
        "n_tokens": "sum",
        "n_lines": "sum",
        "onstage": sort_join_strings,
    }
    df_grouped = df.groupby(groupby).agg(agg).reset_index()
    df_grouped["onstage"] = df_grouped["onstage"].map(character_string_to_sorted_list)
    # for node weights <- lines of speech
    df_speaker_exploded = _explode_df(df, "speaker")
    speaker_weights = (
        df_speaker_exploded.groupby(groupby + ["speaker"])
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
    df_onstage_exploded = _explode_df(df, "onstage")
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
    int_columns = [
        "n_lines_speaker",
        "n_tokens_speaker",
        "n_lines_onstage",
        "n_tokens_onstage",
    ]
    for column in int_columns:
        edge_specific_node_weights[column] = edge_specific_node_weights[column].astype(
            int
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
    """

    :param df:
    :return:
    """
    df_mwd = get_multi_directed_hypergraph_edges(df)
    df_mwd = (
        df_mwd.groupby(["act", "scene", "stagegroup", "speaker", "onstage"])
        .agg(dict(n_tokens=sum, n_lines=sum))
        .reset_index()
    )
    return df_mwd


def _hypergraph_node_dataframe(
    df_exploded_onstage: pd.DataFrame, df_exploded_speaker: pd.DataFrame
) -> pd.DataFrame:
    """

    :param df_exploded_onstage:
    :param df_exploded_speaker:
    :return:
    """
    nodes = pd.DataFrame()
    nodes["node"] = sorted(df_exploded_onstage.onstage.unique())
    nodes["n_lines_onstage"] = nodes.node.map(
        lambda node: df_exploded_onstage.query("onstage == @node").n_lines.sum()
    )
    nodes["n_tokens_onstage"] = nodes.node.map(
        lambda node: df_exploded_onstage.query("onstage == @node").n_tokens.sum()
    )
    nodes["n_lines_speaker"] = nodes.node.map(
        lambda node: df_exploded_speaker.query("speaker == @node").n_lines.sum()
    )
    nodes["n_tokens_speaker"] = nodes.node.map(
        lambda node: df_exploded_speaker.query("speaker == @node").n_tokens.sum()
    )
    column_order = [
        "node",
        "n_tokens_onstage",
        "n_tokens_speaker",
        "n_lines_onstage",
        "n_lines_speaker",
    ]
    return nodes[column_order]


def get_hypergraph_nodes(df: pd.DataFrame) -> pd.DataFrame:
    """

    :param df: pd.DataFrame as loaded from an .agg.csv file
    :return: pd.DataFrame of hypergraph nodes with {tokens,lines} {spoken,heard} as potential global node weights
    """
    df_exploded_onstage = _explode_df(df, "onstage")
    df_exploded_speaker = _explode_df(df, "speaker")
    nodes = _hypergraph_node_dataframe(df_exploded_onstage, df_exploded_speaker)
    return nodes
