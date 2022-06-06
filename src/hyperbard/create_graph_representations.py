import os
from collections import OrderedDict
from glob import glob

import networkx as nx
import pandas as pd
from statics import DATA_PATH, GRAPHDATA_PATH

from hyperbard.graph_representations import (
    get_bipartite_graph,
    get_count_weighted_graph,
    get_weighted_multigraph,
)
from hyperbard.utils import get_filename_base


def node_dataframe(G):
    return pd.DataFrame.from_records(
        [{"node": n, **dict(data)} for n, data in G.nodes(data=True)]
    ).sort_values("node")


def edge_dataframe(G):
    if type(G) == nx.MultiGraph:
        return pd.DataFrame.from_records(
            [
                {
                    "node1": u,
                    "node2": v,
                    "key": key,
                    **dict(data),
                }
                for u, v, key, data in G.edges(keys=True, data=True)
            ]
        ).sort_values(["edge_index", "node1", "node2", "key"])
    elif type(G) == nx.Graph:
        df = pd.DataFrame.from_records(
            [
                {
                    "node1": u,
                    "node2": v,
                    **dict(data),
                }
                for u, v, data in G.edges(data=True)
            ]
        )
        if "edge_index" in df:
            return df.sort_values(["edge_index", "node1", "node2"])
        elif "count" in df:
            return df.sort_values(
                ["node1", "node2", "count"], ascending=[True, True, False]
            )
        else:
            return df.sort_values(["node1", "node2"])


def save_graph(G, representation, path):
    if representation.startswith("ce"):  # clique expansions
        representation_for_nodes = representation.split("-")[0]
        nodes = node_dataframe(G)
        edges = edge_dataframe(G)
    elif representation.startswith("se"):  # star expansions
        if type(G) == nx.Graph:
            representation_for_nodes = "-".join(representation.split("-")[:-1])
            nodes = node_dataframe(G)
            edges = edge_dataframe(G).sort_values(
                ["node2", "node1"]
            )  # node2 is the play part, so sorting by that first is more intuitive
        elif type(G) == nx.MultiDiGraph:  # speech act star expansion
            return  # TODO
    elif representation.startswith("hg"):  # TODO hgs
        return
    else:
        raise NotImplementedError(f"Unknown representation: {representation}")
    nodes.to_csv(f"{path}_{representation_for_nodes}.nodes.csv", index=False)
    edges.to_csv(f"{path}_{representation}.edges.csv", index=False)


def handle_file(file):
    file_base = get_filename_base(file, full=True).split(".")[0]
    print(file_base)
    df = pd.read_csv(file)

    expansions = OrderedDict(
        {
            "ce-scene-mw": {
                "groupby": ["act", "scene"],
                "constructor": get_weighted_multigraph,
            },
            "ce-group-mw": {
                "groupby": ["act", "scene", "stagegroup"],
                "constructor": get_weighted_multigraph,
            },
            "ce-scene-w": {
                "groupby": ["act", "scene"],
                "constructor": get_count_weighted_graph,
            },
            "ce-group-w": {
                "groupby": ["act", "scene", "stagegroup"],
                "constructor": get_count_weighted_graph,
            },
            "se-scene-w": {
                "groupby": ["act", "scene"],
                "constructor": get_bipartite_graph,
            },
            "se-group-w": {
                "groupby": ["act", "scene", "stagegroup"],
                "constructor": get_bipartite_graph,
            },
            "se-speech-mwd": {
                "groupby": ["act", "scene", "stagegroup", "setting", "speaker"],
                "constructor": get_bipartite_graph,
            },
        }
    )
    for representation, parameters in expansions.items():
        G = parameters["constructor"](df, parameters["groupby"])
        save_graph(G, representation, f"{GRAPHDATA_PATH}/{file_base}")


if __name__ == "__main__":
    files = sorted(glob(f"{DATA_PATH}/*.agg.csv"))
    print(f"Found {len(files)} files to process.")
    os.makedirs(GRAPHDATA_PATH, exist_ok=True)

    for file in files:
        handle_file(file)
    # with Pool(cpu_count() - 3) as p:
    #     p.map(handle_file, files)
