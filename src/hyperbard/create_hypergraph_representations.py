import os
from collections import OrderedDict
from glob import glob

import pandas as pd

from hyperbard.hypergraph_representations import (
    get_hypergraph_edges,
    get_hypergraph_nodes,
    get_multi_directed_hypergraph_edges,
    get_weighted_directed_hypergraph_edges,
)
from hyperbard.statics import DATA_PATH, GRAPHDATA_PATH
from hyperbard.utils import get_filename_base


def handle_file(file):
    file_base = get_filename_base(file, full=True).split(".")[0]
    print(file_base)
    df = pd.read_csv(file)
    undirected_expansions = OrderedDict(
        {
            "hg-scene-mw": {
                "groupby": ["act", "scene"],
                "constructor": get_hypergraph_edges,
            },
            "hg-group-mw": {
                "groupby": ["act", "scene", "stagegroup"],
                "constructor": get_hypergraph_edges,
            },
        }
    )
    directed_expansions = OrderedDict(
        {
            "hg-speech-mwd": {
                "constructor": get_multi_directed_hypergraph_edges,
            },
            "hg-speech-wd": {
                "constructor": get_weighted_directed_hypergraph_edges,
            },
        }
    )
    path = f"{GRAPHDATA_PATH}/{file_base}"
    representation_for_nodes = "hg"
    nodes = get_hypergraph_nodes(df)
    nodes.to_csv(f"{path}_{representation_for_nodes}.nodes.csv", index=False)
    for representation, parameters in undirected_expansions.items():
        edges, edge_specific_node_weights = parameters["constructor"](
            df, parameters["groupby"]
        )
        edges.to_csv(f"{path}_{representation}.edges.csv", index=False)
        edge_specific_node_weights.to_csv(
            f"{path}_{representation}.node-weights.csv", index=False
        )
    for representation, parameters in directed_expansions.items():
        edges = parameters["constructor"](df)
        edges.to_csv(f"{path}_{representation}.edges.csv", index=False)


if __name__ == "__main__":
    files = sorted(glob(f"{DATA_PATH}/*.agg.csv"))
    print(f"Found {len(files)} files to process.")
    os.makedirs(GRAPHDATA_PATH, exist_ok=True)

    for file in files:
        handle_file(file)
    # with Pool(cpu_count() - 3) as p:
    #     p.map(handle_file, files)
