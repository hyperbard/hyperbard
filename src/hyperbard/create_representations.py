import os
from glob import glob
from multiprocessing import Pool, cpu_count

import networkx as nx
import pandas as pd
from statics import DATA_PATH, GRAPHDATA_PATH

from hyperbard.representations import (
    get_bipartite_graph,
    get_count_weighted_graph,
    get_hypergraph,
    get_weighted_multigraph,
)
from hyperbard.utils import get_filename_base


def get_node_string(node):
    if type(node) == str:
        return node
    elif type(node) == tuple:
        return ".".join(str(elem) for elem in node)
    else:
        raise ValueError(f"Unexpected node type: {type(node)}!")


def node_dataframe(G):
    return pd.DataFrame.from_records(
        [{"node": get_node_string(n), **dict(data)} for n, data in G.nodes(data=True)]
    ).sort_values("node")


def save_graph(G, representation, path):
    if type(G) == nx.MultiGraph:  # clique expansions
        representation_for_nodes = representation.split("-")[0]
        nodes = node_dataframe(G)
        edges = pd.DataFrame.from_records(
            [
                {
                    "node1": get_node_string(u),
                    "node2": get_node_string(v),
                    "key": key,
                    **dict(data),
                }
                for u, v, key, data in G.edges(keys=True, data=True)
            ]
        ).sort_values(["scene_index", "node1", "node2", "key"])
    elif type(G) == nx.Graph:  # simple star expansions
        representation_for_nodes = "-".join(representation.split("-")[:-1])
        nodes = node_dataframe(G)
        edges = pd.DataFrame.from_records(
            [
                {"node1": get_node_string(u), "node2": get_node_string(v), **dict(data)}
                for u, v, data in G.edges(data=True)
            ]
        ).sort_values(["node2", "node1"])
    elif type(G) == nx.MultiDiGraph:  # speech act star expansion
        return  # TODO
    else:
        return  # TODO hgs
    nodes.to_csv(f"{path}_{representation_for_nodes}.nodes.csv", index=False)
    edges.to_csv(f"{path}_{representation}.edges.csv", index=False)


def handle_file(file):
    file_base = get_filename_base(file, full=True).split(".")[0]
    print(file_base)
    df = pd.read_csv(file)

    expansions = {
        "ce-scene-mw": {
            "groupby": ["act", "scene"],
            "constructor": get_weighted_multigraph,
        },
        "ce-group-mw": {
            "groupby": ["act", "scene", "stagegroup"],
            "constructor": get_weighted_multigraph,
        },
        "se-scene-w": {"groupby": ["act", "scene"], "constructor": get_bipartite_graph},
        "se-group-w": {
            "groupby": ["act", "scene", "stagegroup"],
            "constructor": get_bipartite_graph,
        },
        "se-speech-mwd": {
            "groupby": ["act", "scene", "stagegroup", "setting", "speaker"],
            "constructor": get_bipartite_graph,
        },
    }
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
