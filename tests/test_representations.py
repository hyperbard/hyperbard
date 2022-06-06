from unittest import TestCase

from hyperbard.representations import (
    get_bipartite_graph,
    get_count_weighted_graph,
    get_hypergraph,
    get_weighted_multigraph,
)
from tests.xml_testcase import XMLTestCase


class RepresentationsTest(XMLTestCase):
    def test_get_weighted_multigraph(self):
        groupby = ["act", "scene"]
        G = get_weighted_multigraph(self.toy_agg_df, groupby)
        self.assertEqual(G.number_of_nodes(), 8)
        self.assertEqual(G.number_of_edges(), 48)
        self.assertEqual(
            G.get_edge_data("#ATTENDANTS_MND", "#Hippolyta_MND", 0)["n_lines"], 11
        )
        self.assertEqual(
            G.get_edge_data("#ATTENDANTS_MND", "#Hippolyta_MND", 1)["n_lines"], 2
        )
        self.assertEqual(
            G.get_edge_data("#ATTENDANTS_MND", "#Hippolyta_MND", 2)["n_lines"], 1
        )
        groupby = ["act", "scene", "stagegroup"]
        G = get_weighted_multigraph(self.toy_agg_df, groupby)
        self.assertEqual(G.number_of_nodes(), 8)
        self.assertEqual(G.number_of_edges(), 51)
        self.assertEqual(
            G.get_edge_data("#ATTENDANTS_MND", "#Hippolyta_MND", 0)["n_lines"], 5
        )

    def test_get_count_weighted_graph(self):
        groupby = ["act", "scene"]
        G = get_count_weighted_graph(self.toy_agg_df, groupby)
        self.assertEqual(G.number_of_nodes(), 8)
        self.assertEqual(G.number_of_edges(), 24)
        self.assertEqual(
            G.get_edge_data("#ATTENDANTS_MND", "#Hippolyta_MND")["count"], 3
        )
        groupby = ["act", "scene", "stagegroup"]
        G = get_count_weighted_graph(self.toy_agg_df, groupby)
        self.assertEqual(G.number_of_nodes(), 8)
        self.assertEqual(G.number_of_edges(), 24)
        self.assertEqual(
            G.get_edge_data("#ATTENDANTS_MND", "#Hippolyta_MND")["count"], 3
        )

    def test_get_bipartite_graph(self):
        groupby = ["act", "scene"]
        G = get_bipartite_graph(self.toy_agg_df, groupby)
        self.assertEqual(G.number_of_nodes(), 11)
        self.assertEqual(G.number_of_edges(), 18)
        groupby = ["act", "scene", "stagegroup"]
        G = get_bipartite_graph(self.toy_agg_df, groupby)
        self.assertEqual(G.number_of_nodes(), 12)
        self.assertEqual(G.number_of_edges(), 21)
