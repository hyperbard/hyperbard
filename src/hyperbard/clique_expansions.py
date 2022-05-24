from glob import glob
from itertools import combinations

import seaborn as sns

sns.set_style("whitegrid")

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from matplotlib import cm

from hyperbard.preprocessing import get_filename_base
from hyperbard.statics import DATA_PATH, GRAPHICS_PATH


def character_string_to_sorted_list(character_string):
    return sorted(set(character_string.split()))


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


def degree_centrality(G, weight=None):
    """
    Wrapper around nx.degree_centrality that allows to account for weights.
    When weight attribute is specified, returns fraction of degree sum in which node participates.
    """
    if weight is None:
        return nx.degree_centrality(G)
    else:
        assert (
            weight in list(G.edges(data=True))[0][-1].keys()
        ), f"Attribute '{weight}'\
        is not an edge attribute! Edge attributes are: {list(list(G.edges(data=True))[0][-1].keys())}"
        s = 1.0 / sum(dict(G.degree(weight=weight)).values())
        centrality = {n: d * s for n, d in G.degree(weight=weight)}
        return centrality


def centrality_ranking(G, weight=None):
    return sorted(
        degree_centrality(G, weight).items(), key=lambda tup: tup[-1], reverse=True
    )


def centrality_ranking_with_equalities(G, weight=None):
    """
    output: list of tuples [({set of characters}, centrality), ...], sorted by centrality descending
    """
    ranking_list = centrality_ranking(G, weight)
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
    ranks = {
        "02_act_scene_multi": character_rank_dictionary(
            centrality_ranking_with_equalities(mG)
        ),
        "04_act_scene_stagegroup_multi": character_rank_dictionary(
            centrality_ranking_with_equalities(mG2)
        ),
        "01_act_scene_simple": character_rank_dictionary(
            centrality_ranking_with_equalities(G)
        ),
        "03_act_scene_stagegroup_simple": character_rank_dictionary(
            centrality_ranking_with_equalities(G2)
        ),
    }
    return pd.DataFrame.from_records(ranks).reset_index()


def plot_character_rankings(df, save_path=None):
    """
    baby plotting function (wip!)
    """
    character_ranking_df = get_character_ranking_df(df)
    fig, ax = plt.subplots(1, 1, figsize=(12, 9 + len(character_ranking_df) // 10))
    pd.plotting.parallel_coordinates(
        character_ranking_df, class_column="index", colormap=cm.viridis, ax=ax
    )
    ax.invert_yaxis()
    plt.legend(loc=(1, 0))
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, transparent=True)
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
