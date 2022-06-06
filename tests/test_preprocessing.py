import math
import os.path
from unittest import TestCase

import pandas as pd

from hyperbard.preprocessing import (
    get_agg_xml_df,
    get_aggregated,
    get_attrs,
    get_body,
    get_cast_df,
    get_descendants_ids,
    get_grouped_df,
    get_raw_xml_df,
    get_soup,
    get_who_attributes,
    get_xml_df,
    has_speaker,
    is_descendant_of_redundant_element,
    is_entrance,
    is_exit,
    is_leaf,
    is_navigable_string,
    is_new_act,
    is_redundant_element,
    keep_elem_in_xml_df,
    set_act,
    set_onstage,
    set_scene,
    set_setting,
    set_speaker,
    set_stagegroup,
)
from tests.xml_testcase import XMLTestCase


class PreprocessingTest(XMLTestCase):
    def test_get_agg_xml_df(self):
        df = get_raw_xml_df(self.toy_xml_file)
        agg_df = get_agg_xml_df(df)
        self.assertEqual(len(agg_df), 2)
        self.assertEqual(agg_df.at[0, "setting"], 1)
        self.assertEqual(agg_df.at[0, "n_tokens"], 14)
        self.assertEqual(agg_df.at[1, "n_tokens"], 2)
        self.assertEqual(agg_df.at[0, "n_lines"], 2)
        self.assertEqual(agg_df.at[1, "n_lines"], 1)
        self.assertEqual(agg_df.at[0, "stagegroup"], 1)
        self.assertEqual(agg_df.at[1, "stagegroup"], 1)

    def test_get_aggregated(self):
        raw_df = get_raw_xml_df(self.toy_xml_file)
        agg_df = get_aggregated(raw_df)
        self.assertEqual(agg_df.at[0, "n"], "1.1.1")
        self.assertEqual(agg_df.at[1, "n"], "1.1.2")
        self.assertEqual(agg_df.at[2, "n"], "1.1.12")
        self.assertEqual(
            agg_df.at[0, "onstage"],
            "#ATTENDANTS_MND #Hippolyta_MND #Philostrate_MND #Theseus_MND",
        )
        self.assertEqual(agg_df.at[0, "speaker"], "#Theseus_MND")
        self.assertEqual(agg_df.at[0, "n_tokens"], 6)
        self.assertEqual(agg_df.at[0, "xml:id"], "fs-mnd-0000250")

    def test_get_body(self):
        self.assertEqual(get_body(self.soup).parent.name, "text")
        self.assertEqual(get_body(self.soup).find_all("w")[0].get_text(), "ACT")

    def test_get_attrs(self):
        elem_notext = self.soup.find("div")
        self.assertTrue(math.isnan(get_attrs(elem_notext)["text"]))
        self.assertEqual(
            {k: v for k, v in get_attrs(elem_notext).items() if k != "text"},
            {"tag": "div", "type": "act", "n": "1"},
        )
        elem_text = self.soup.find("w")
        self.assertEqual(
            get_attrs(elem_text),
            {"tag": "w", "xml:id": "fs-mnd-0000010", "text": "ACT"},
        )

    def test_get_descendants_ids(self):
        self.assertListEqual(
            get_descendants_ids(self.soup.find("stage")),
            [
                "fs-mnd-0000070",
                "fs-mnd-0000090",
                "fs-mnd-0000100",
                "fs-mnd-0000120",
                "fs-mnd-0000130",
                "fs-mnd-0000150",
                "fs-mnd-0000170",
                "fs-mnd-0000180",
                "fs-mnd-0000200",
                "fs-mnd-0000220",
                "fs-mnd-0000230",
            ],
        )

    def test_get_grouped_df(self):
        df = get_raw_xml_df(self.toy_xml_file)
        aggregated = get_aggregated(df)
        set_setting(aggregated)
        grouped = get_grouped_df(aggregated)
        self.assertEqual(len(grouped), 2)
        self.assertEqual(grouped.at[0, "setting"], 1)
        self.assertEqual(grouped.at[0, "n_tokens"], 14)
        self.assertEqual(grouped.at[1, "n_tokens"], 2)
        self.assertEqual(grouped.at[0, "n_lines"], 2)
        self.assertEqual(grouped.at[1, "n_lines"], 1)
        self.assertEqual(grouped.at[0, "stagegroup"], 1)
        self.assertEqual(grouped.at[1, "stagegroup"], 1)

    def test_get_soup(self):
        self.assertTrue(bool(get_soup(self.toy_xml_file).text))
        self.assertEqual(
            get_soup(self.toy_xml_file).find_all("w")[-1].get_text(), "Demetrius"
        )

    def test_get_who_attributes(self):
        self.assertEqual(get_who_attributes(self.soup.find("sp")), "#Theseus_MND")
        self.assertTrue(math.isnan(get_who_attributes(self.soup.find("w"))))

    def test_get_cast_df(self):
        cast_df = get_cast_df(self.toy_cast_file)
        self.assertEqual(len(cast_df), 11)
        self.assertEqual(cast_df.at[0, "xml:id"], "ATTENDANTS.0.1_MND")
        self.assertEqual(cast_df.at[0, "corresp"], "#ATTENDANTS_MND")

    def test_get_xml_df(self):
        self.assertEqual(len(get_xml_df(get_body(self.soup)).query("tag == 'l'")), 3)
        self.assertEqual(
            len(get_xml_df(get_body(self.soup)).query("tag == 'stage'")), 3
        )
        self.assertEqual(len(get_xml_df(get_body(self.soup)).query("tag == 'sp'")), 2)
        self.assertEqual(len(get_xml_df(get_body(self.soup)).query("tag == 'w'")), 35)

    def test_has_speaker(self):
        xml_df = get_xml_df(get_body(self.soup))
        self.assertTrue(has_speaker(xml_df.query("tag == 'sp'").iloc[0]))
        self.assertFalse(has_speaker(xml_df.query("tag == 'w'").iloc[0]))

    def test_is_descendant_of_redundant_element(self):
        elem_descendant_of_redundant = self.soup.find("w")
        elem_no_descendant_of_redundant = self.soup.find("div")
        self.assertTrue(
            is_descendant_of_redundant_element(elem_descendant_of_redundant)
        )
        self.assertFalse(
            is_descendant_of_redundant_element(elem_no_descendant_of_redundant)
        )

    def test_is_entrance(self):
        xml_df = get_xml_df(get_body(self.soup))
        for idx, row in xml_df.query(
            "tag == 'stage' and type == 'entrance'"
        ).iterrows():
            self.assertTrue(is_entrance(row))

    def test_is_exit(self):
        xml_df = get_xml_df(get_body(self.soup))
        for idx, row in xml_df.query("tag == 'stage' and type == 'exit'").iterrows():
            self.assertTrue(is_exit(row))

    def test_is_leaf(self):
        elem_leaf = self.soup.find("w")
        elem_nonleaf = self.soup.find("div")
        self.assertTrue(is_leaf(elem_leaf))
        self.assertFalse(is_leaf(elem_nonleaf))

    def test_is_navigable_string(self):
        elem_no_navigable_string = self.soup.find("w")
        elem_navigable_string = self.soup.find("w").contents[0]
        self.assertFalse(is_navigable_string(elem_no_navigable_string))
        self.assertTrue(is_navigable_string(elem_navigable_string))

    def test_is_new_act(self):
        xml_df = get_xml_df(get_body(self.soup))
        set_act(xml_df)
        self.assertTrue(is_new_act(xml_df.query("tag == 'sp'").iloc[0], 0))
        self.assertFalse(is_new_act(xml_df.query("tag == 'sp'").iloc[0], 1))

    def test_is_redundant_element(self):
        elem_reduntant = self.soup.find("head")
        elem_nonredundant = self.soup.find("div")
        self.assertTrue(is_redundant_element(elem_reduntant))
        self.assertFalse(is_redundant_element(elem_nonredundant))

    def test_keep_elem_in_xml_df(self):
        elem_keep = self.soup.find("div")
        elem_nokeep = self.soup.find("head")
        self.assertTrue(keep_elem_in_xml_df(elem_keep))
        self.assertFalse(keep_elem_in_xml_df(elem_nokeep))

    def test_set_act(self):
        xml_df = get_xml_df(get_body(self.soup))
        set_act(xml_df)
        self.assertListEqual(list(xml_df.query("type == 'act'")["act"]), [1])
        self.assertFalse(any(pd.isna(x) for x in xml_df["act"]))
        pass

    def test_set_onstage(self):
        xml_df = get_xml_df(get_body(self.soup))
        set_act(xml_df)
        set_scene(xml_df)
        set_onstage(xml_df)
        self.assertEqual(
            xml_df.query("tag == 'stage'").iloc[0]["onstage"],
            "#ATTENDANTS_MND #Hippolyta_MND #Philostrate_MND #Theseus_MND",
        )

    def test_set_scene(self):
        xml_df = get_xml_df(get_body(self.soup))
        set_act(xml_df)
        set_scene(xml_df)
        self.assertTrue(set(xml_df.query("type == 'act'")["scene"]) == {0})
        self.assertFalse(0 in set(xml_df.query("type != 'act'")["scene"]))
        self.assertFalse(any(pd.isna(x) for x in xml_df["scene"]))

    def test_set_setting(self):
        raw_df = get_raw_xml_df(self.toy_xml_file)
        agg_df = get_aggregated(raw_df)
        set_setting(agg_df)
        self.assertSetEqual(set(agg_df.setting), {1, 2})

    def test_set_speaker(self):
        xml_df = get_xml_df(get_body(self.soup))
        set_act(xml_df)
        set_scene(xml_df)
        set_onstage(xml_df)
        set_stagegroup(xml_df)
        set_speaker(xml_df, get_body(self.soup))
        self.assertEqual(xml_df.query("tag == 'sp'").iloc[0]["speaker"], "#Theseus_MND")
        self.assertEqual(xml_df.query("tag == 'l'").iloc[0]["speaker"], "#Theseus_MND")
        self.assertEqual(
            xml_df[xml_df["xml:id"] == "ftln-0012"].iloc[0]["speaker"],
            "#Philostrate_MND",
        )

    def test_set_stagegroup(self):
        xml_df = get_xml_df(get_body(self.soup))
        set_act(xml_df)
        set_scene(xml_df)
        set_onstage(xml_df)
        set_stagegroup(xml_df)
        self.assertEqual(len(xml_df.stagegroup_raw.unique()), 3)
        self.assertSetEqual(
            set(xml_df.query("tag == 'div' and n == '1'")["stagegroup_raw"].unique()),
            {0},
        )
        self.assertSetEqual(
            set(xml_df.query("n == 'SD 1.1.0'")["stagegroup_raw"].unique()), {1}
        )
        self.assertSetEqual(
            set(xml_df.query("n == 'SD 1.1.20.1'")["stagegroup_raw"].unique()), {2}
        )
