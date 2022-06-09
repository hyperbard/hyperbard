"""I/O routines for graphs and hypergraphs."""

import os
import re

import hypernetx as hnx
import networkx as nx
import pandas as pd
from statics import GRAPHDATA_PATH


def prettify_identifier(identifier):
    """Return pretty identifier (character name)."""
    identifier = identifier.replace("#", "").split("_")[0]
    # Remove any prefixes that precede the current one if they are
    # written in capital letters. This removes "SERVANTS.CAPULET."
    # in Romeo & Juliet, for instance.
    identifier = re.sub(r"[A-Z\.]*([A-Z])", r"\1", identifier)
    return identifier


def load_graph(play, representation, edge_weights=None):
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
    graph_type = representation.split("-")[0]
    agg_type = representation.split("-")[1]

    assert graph_type in ["ce", "se"], RuntimeError("Unexpected graph type")

    nodes_file = os.path.join(GRAPHDATA_PATH, f"{play}_{graph_type}.nodes.csv")
    edges_file = os.path.join(GRAPHDATA_PATH, f"{play}_{representation}.edges.csv")

    # Use special representations for getting the nodes of star expansions
    if graph_type == "se":
        nodes_repr = "-".join(representation.split("-")[:2])
        nodes_file = os.path.join(GRAPHDATA_PATH, f"{play}_{nodes_repr}.nodes.csv")

    nodes = pd.read_csv(nodes_file)
    edges = pd.read_csv(edges_file)

    edges = edges.rename(
        {
            "source": "node1",
            "target": "node2",
        },
        axis="columns",
    )

    # Get nice character names to stay more true to the raw data instead
    # of spewing out additional tokens.
    nodes.node = nodes.node.map(prettify_identifier)
    edges.node1 = edges.node1.map(prettify_identifier)

    # Coercing this to a `str` is at best a NOP; it only ever applies to
    # the star expansion.
    edges.node2 = edges.node2.astype(str)
    edges.node2 = edges.node2.map(prettify_identifier)

    nodes = nodes.query("not node.str.isupper()")
    edges = edges.query("not node1.str.isupper() and not node2.str.isupper()")

    # Check type of graph to create in order to potentially support
    # multi-edges.
    prop_type = representation.split("-")[2]

    if agg_type != "speech":

        if prop_type.startswith("m"):
            G = nx.MultiGraph()
        else:
            G = nx.Graph()

        if graph_type == "ce":
            G.add_nodes_from(nodes.node)
        elif graph_type == "se":
            G.add_nodes_from(edges.node1, node_type="character")
            G.add_nodes_from(edges.node2, node_type="text_unit")
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
        if attribute != edge_weights:
            values = dict(edges_indexed[attribute])
            nx.set_edge_attributes(G, values, name=attribute)

    return G


def find_key_columns(G):
    if isinstance(G, nx.MultiDiGraph):
        return ["node1", "node2", "key"]
    elif isinstance(G, nx.MultiGraph):
        return ["node1", "node2", "key"]
    elif isinstance(G, nx.DiGraph):
        return ["node1", "node2"]
    elif isinstance(G, nx.Graph):
        return ["node1", "node2"]
    else:
        raise ValueError(f"Unexpected graph type: {type(G)}")


def load_hypergraph(play, representation, edge_weights=None):
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
    hypergraph_type = representation.split("-")[0]
    agg_type = representation.split("-")[1]

    assert hypergraph_type == "hg", RuntimeError("Expecting hypergraph representation")

    edges_file = os.path.join(GRAPHDATA_PATH, f"{play}_{representation}.edges.csv")
    edges = pd.read_csv(edges_file)

    edges.onstage = edges.onstage.map(
        lambda x: list(map(prettify_identifier, x.split()))
    ).map(lambda onstage: [x for x in onstage if not x.isupper()])

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
