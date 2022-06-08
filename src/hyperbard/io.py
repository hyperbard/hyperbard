"""I/O routines for graphs and hypergraphs."""

import os

import networkx as nx
import pandas as pd

from statics import GRAPHDATA_PATH

def prettify_identifier(identifier):
    return identifier.replace("#", "").split("_")[0]


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
    graph_type = representation.split('-')[0]

    assert graph_type in ['ce', 'se'], RuntimeError('Unexpected graph type')

    nodes_file = os.path.join(GRAPHDATA_PATH, f'{play}_{graph_type}.nodes.csv')
    edges_file = os.path.join(GRAPHDATA_PATH, f'{play}_{representation}.edges.csv')

    nodes = pd.read_csv(nodes_file)
    edges = pd.read_csv(edges_file)

    # Get nice character names to stay more true to the raw data instead
    # of spewing out additional tokens.
    nodes.node = nodes.node.map(prettify_identifier)
    edges.node1 = edges.node1.map(prettify_identifier)
    edges.node2 = edges.node2.map(prettify_identifier)

    G = nx.Graph()
    G.add_nodes_from(nodes.node)

    if edge_weights is None:
        G.add_edges_from(zip(edges.node1, edges.node2))
    else:
        G.add_weighted_edges_from(
            zip(edges.node1, edges.node2, edges[edge_weights])
        )

    print(nodes)
    print(edges)
    print(G)

    return G
