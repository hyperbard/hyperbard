from glob import glob
from itertools import combinations

import numpy as np
import seaborn as sns

sns.set_style("whitegrid")

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import regex as re
from matplotlib import cm

from hyperbard.preprocessing import get_filename_base
from hyperbard.statics import DATA_PATH, GRAPHICS_PATH


def character_string_to_sorted_list(character_string):
    return sorted(set(character_string.split()))


def split_identifier(character_string):
    return re.split("_.*?$", character_string, maxsplit=1)[0].replace("#", "")


def join_strings(list_of_strings):
    return " ".join(list_of_strings)


def get_weighted_multigraph(df: pd.DataFrame, groupby: list):
    """
    groupby = ["act", "scene"] -> one edge per act and scene
    groupby = ["act", "scene", "stagegroup"] -> one edge per act, scene, and stagegroup
    multi-edges are kept, with n_tokens or n_lines as potential weights
    """
    agg = dict(onstage=join_strings, n_tokens=sum, n_lines=sum)
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
    agg = dict(onstage=join_strings, n_tokens=sum, n_lines=sum)
    df_aggregated = df.groupby(groupby).agg(agg).reset_index()
    df_aggregated["onstage"] = df_aggregated["onstage"].map(
        character_string_to_sorted_list
    )
    if groupby != ["act", "scene", "stagegroup", "setting", "speaker"]:
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
    else:
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
            row_speaker = row["speaker"]
            row_lines = row["n_lines"]
            row_tokens = row["n_tokens"]
            G.add_edge(row_speaker, row_node, n_lines=row_lines, n_tokens=row_tokens)
            G.add_edges_from(
                [
                    (row_node, character)
                    for character in row["onstage"]
                    if character != row_speaker
                ],
                n_lines=row_lines,
                n_tokens=row_tokens,
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


def plot_character_rankings(df, save_path=None):
    """
    baby plotting function (wip!)
    """
    character_ranking_df = get_character_ranking_df(df)
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(
            3 * (len(character_ranking_df.columns) - 1),
            9 + len(character_ranking_df) // 10,
        ),
    )
    ax.set_prop_cycle(linestyle=["-", "--", ":", "-."], marker=["^", ">", "v", "<"])
    pd.plotting.parallel_coordinates(
        character_ranking_df,
        class_column="index",
        colormap=cm.viridis,
        ax=ax,
        alpha=0.5,
    )
    ax.invert_yaxis()
    labels = [split_identifier(elem.get_text()) for elem in ax.legend().get_texts()]
    plt.legend(loc=(1, 0), labels=labels)
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, transparent=True, bbox_inches="tight", backend="pgf")
        plt.close()


def plot_correlation_matrix(df, save_path=None):
    character_ranking_df = get_character_ranking_df(df)
    character_ranking_df_indexed = character_ranking_df.set_index("index")
    vmin = min(
        character_ranking_df_indexed.corr("spearman").min().min(),
        character_ranking_df_indexed.corr("kendall").min().min(),
    )
    sns.heatmap(
        character_ranking_df_indexed.corr("kendall"),
        square=True,
        cmap=cm.Reds,
        cbar_kws=dict(shrink=0.8),
        mask=np.tril(character_ranking_df_indexed.corr("kendall").values, k=0).astype(
            bool
        ),
        vmin=vmin,
        vmax=1.0,
        cbar=False,
    )
    sns.heatmap(
        character_ranking_df_indexed.corr("spearman"),
        square=True,
        cmap=cm.Reds,
        cbar_kws=dict(shrink=0.8),
        mask=np.triu(character_ranking_df_indexed.corr("spearman").values, k=0).astype(
            bool
        ),
        vmin=vmin,
        vmax=1.0,
    )
    plt.title("upper triangle: kendall, lower triangle: spearman")
    if save_path is not None:
        plt.savefig(save_path, transparent=True, backend="pgf", bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    files = sorted(glob(f"{DATA_PATH}/*agg.csv"))
    for file in files:
        file_short = get_filename_base(file).split("_")[0]
        print(file_short)
        df = pd.read_csv(file)
        plot_character_rankings(
            df, save_path=f"{GRAPHICS_PATH}/{file_short}_clique_expansions.pdf"
        )
        plot_correlation_matrix(
            df, save_path=f"{GRAPHICS_PATH}/{file_short}_ranking_correlations.pdf"
        )
