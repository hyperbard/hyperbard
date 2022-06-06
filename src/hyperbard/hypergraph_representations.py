import hypernetx as hnx
import pandas as pd
from utils import character_string_to_sorted_list, sort_join_strings


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
