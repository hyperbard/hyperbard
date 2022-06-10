"""I/O routines for graphs and hypergraphs."""

import os
import re

import hypernetx as hnx
import networkx as nx
import pandas as pd

from hyperbard.statics import GRAPHDATA_PATH
from hyperbard.utils import remove_uppercase_prefixes


def rename_directed_columns(edges):
    return edges.rename(
        {
            "source": "node1",
            "target": "node2",
        },
        axis="columns",
    )


def load_graph(
    play, representation, edge_weights=None, restrict_to_named_characters=True
):
    """Load graph for a specific representation of a play.

    Parameters
    ----------
    play : str
        Identifier of the play, e.g. 'romeo-and-juliet'.

    representation : str
        Graph representation identifier, e.g. 'ce-group-mw'.

    edge_weights : None or str
        Optional attribute to use for assigning edge weights.

    Returns
    -------
    nx.Graph
        Graph corresponding to the specified play and representation.
    """
    assert len(representation.split("-")) == 3, RuntimeError(
        f"Unexpected representation string: {representation}, expected 3 components!"
    )

    graph_type, agg_type, prop_type = representation.split("-")

    assert graph_type in ["ce", "se"], RuntimeError(
        f"Unexpected graph type: {graph_type}"
    )
    assert agg_type in ["scene", "group", "speech"], RuntimeError(
        f"Unexpected aggregation type: {agg_type}"
    )

    if graph_type == "ce":
        nodes_file = os.path.join(GRAPHDATA_PATH, f"{play}_{graph_type}.nodes.csv")
    else:  # i.e., graph_type == "se":
        nodes_repr = "-".join(representation.split("-")[:2])
        nodes_file = os.path.join(GRAPHDATA_PATH, f"{play}_{nodes_repr}.nodes.csv")
    edges_file = os.path.join(GRAPHDATA_PATH, f"{play}_{representation}.edges.csv")

    nodes = pd.read_csv(nodes_file)
    edges = pd.read_csv(edges_file)

    edges = rename_directed_columns(edges)

    # Coercing this to a `str` is at best a NOP; it only ever applies to
    # the star expansion.
    edges.node2 = edges.node2.astype(str)

    if restrict_to_named_characters:
        named_nodes = [
            tup[0]
            for tup in filter(
                lambda tup: not tup[-1].isupper(),
                zip(nodes.node, nodes.node.map(remove_uppercase_prefixes)),
            )
        ]
        nodes = nodes.query("node in @named_nodes").copy()
        edges = edges.query("node1 in @named_nodes and node2 in @named_nodes").copy()

    # TODO the if-else branches on unintuitive decisions
    if agg_type != "speech":
        if prop_type.startswith("m"):
            G = nx.MultiGraph()
        else:
            G = nx.Graph()

        if graph_type == "ce":
            G.add_nodes_from(nodes.node)
        elif graph_type == "se":
            G.add_nodes_from(
                nodes.query("node_type == 'character'").node, node_type="character"
            )
            G.add_nodes_from(
                nodes.query("node_type == 'text_unit'").node, node_type="text_unit"
            )
    else:
        if prop_type.startswith("m"):
            G = nx.MultiDiGraph()
        else:
            G = nx.DiGraph()

        for _, row in nodes.iterrows():
            G.add_node(row.node, node_type=row["node_type"])

    if edge_weights is None:
        G.add_edges_from(zip(edges.node1, edges.node2))
    else:
        G.add_weighted_edges_from(
            zip(edges.node1, edges.node2, edges[edge_weights]),
            weight=edge_weights,
        )
    key_columns = find_key_columns(G)
    attribute_columns = [c for c in edges.columns if c not in key_columns]
    edges_indexed = edges.set_index(key_columns)
    for attribute in attribute_columns:
        values = dict(edges_indexed[attribute])
        nx.set_edge_attributes(G, values, name=attribute)

    return G


def find_key_columns(G):
    if isinstance(G, nx.MultiDiGraph) or isinstance(G, nx.MultiGraph):
        key_columns = ["node1", "node2", "key"]
    elif isinstance(G, nx.DiGraph) or isinstance(G, nx.Graph):
        key_columns = ["node1", "node2"]
    else:
        raise ValueError(f"Unexpected graph type: {type(G)}")
    return key_columns


def load_hypergraph(
    play, representation, edge_weights=None, restrict_to_named_characters=True
):
    """Load specific hypergraph representation for a play.

    Parameters
    ----------
    play : str
        Identifier of the play, e.g. 'romeo-and-juliet'.

    representation : str
        Hypergraph representation identifier, e.g. 'hg-group-mw'.

    edge_weights : None or str
        Optional attribute to use for assigning edge weights.

    Returns
    -------
    hnx.Hypergraph
        Hypergraph corresponding to the specified play and representation.
    """
    assert len(representation.split("-")) == 3, RuntimeError(
        f"Unexpected representation string: {representation}, expected 3 components!"
    )

    hypergraph_type, agg_type, prop_type = representation.split("-")

    assert hypergraph_type == "hg", RuntimeError("Expecting hypergraph representation")

    edges_file = os.path.join(GRAPHDATA_PATH, f"{play}_{representation}.edges.csv")
    edges = pd.read_csv(edges_file)

    edges.onstage = edges.onstage.map(lambda x: x.split()).map(
        lambda onstage: [x for x in onstage if not x.isupper()]
    )

    if restrict_to_named_characters:
        named_characters = {
            elem
            for sublist in edges.onstage
            for elem in sublist
            if not remove_uppercase_prefixes(elem).isupper()
        }
        edges.onstage = edges.onstage.map(
            lambda characters: [elem for elem in characters if elem in named_characters]
        )

    H = hnx.Hypergraph()
    for idx, row in edges.iterrows():
        H.add_edge(
            hnx.Entity(
                idx,
                row["onstage"],
                **{k: v for k, v in row.items() if k != "onstage"},
            )
        )

    return H
