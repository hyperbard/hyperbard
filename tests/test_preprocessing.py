import math
import os.path
from unittest import TestCase

import pandas as pd

from hyperbard.preprocessing import (
    get_agg_xml_df,
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


class PreprocessingTest(TestCase):
    def setUp(self) -> None:
        self.toy_xml_file = "tei_toy.xml"
        self.toy_xml_text = """
        <?xml-model href="https://raw.githubusercontent.com/TEIC/TEI-Simple/master/teisimple.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <text>
    <body>
        <div type="act" n="1">
        <head>
          <w xml:id="fs-mnd-0000010">ACT</w>
          <c> </c>
          <w xml:id="fs-mnd-0000030">1</w>
        </head>
        <div type="scene" n="1">
          <head>
            <w xml:id="fs-mnd-0000040">Scene</w>
            <c> </c>
            <w xml:id="fs-mnd-0000060">1</w>
          </head>
          <stage xml:id="stg-0000" n="SD 1.1.0" type="entrance" who="#Theseus_MND #Hippolyta_MND #Philostrate_MND #ATTENDANTS_MND">
            <w xml:id="fs-mnd-0000070" n="SD 1.1.0">Enter</w>
            <c> </c>
            <w xml:id="fs-mnd-0000090" n="SD 1.1.0">Theseus</w>
            <pc xml:id="fs-mnd-0000100" n="SD 1.1.0">,</pc>
            <c> </c>
            <w xml:id="fs-mnd-0000120" n="SD 1.1.0">Hippolyta</w>
            <pc xml:id="fs-mnd-0000130" n="SD 1.1.0">,</pc>
            <c> </c>
            <w xml:id="fs-mnd-0000150" n="SD 1.1.0">and</w>
            <c> </c>
            <w xml:id="fs-mnd-0000170" n="SD 1.1.0">Philostrate</w>
            <pc xml:id="fs-mnd-0000180" n="SD 1.1.0">,</pc>
            <c> </c>
            <w xml:id="fs-mnd-0000200" n="SD 1.1.0">with</w>
            <c> </c>
            <w xml:id="fs-mnd-0000220" n="SD 1.1.0">others</w>
            <pc xml:id="fs-mnd-0000230" n="SD 1.1.0">.</pc>
          </stage>
          <sp xml:id="sp-0001" who="#Theseus_MND">
            <speaker xml:id="spk-0001">
              <w xml:id="fs-mnd-0000240">THESEUS</w>
            </speaker>
            <l xml:id="ftln-0001" n="1.1.1">
              <w xml:id="fs-mnd-0000250" n="1.1.1" lemma="now" ana="#av">Now</w>
              <pc xml:id="fs-mnd-0000260" n="1.1.1">,</pc>
              <c> </c>
              <w xml:id="fs-mnd-0000280" n="1.1.1" lemma="fair" ana="#j">fair</w>
              <c> </c>
              <w xml:id="fs-mnd-0000300" n="1.1.1" lemma="Hippolyta" ana="#n1-nn">Hippolyta</w>
              <pc xml:id="fs-mnd-0000310" n="1.1.1">,</pc>
              <c> </c>
              <w xml:id="fs-mnd-0000330" n="1.1.1" lemma="our" ana="#po">our</w>
              <c> </c>
              <w xml:id="fs-mnd-0000350" n="1.1.1" lemma="nuptial" ana="#j">nuptial</w>
              <c> </c>
              <w xml:id="fs-mnd-0000370" n="1.1.1" lemma="hour" ana="#n1">hour</w>
            </l>
            <l xml:id="ftln-0002" n="1.1.2">
              <w xml:id="fs-mnd-0000380" n="1.1.2" lemma="draw" ana="#vvz">Draws</w>
              <c> </c>
              <w xml:id="fs-mnd-0000400" n="1.1.2" lemma="on" ana="#acp-p">on</w>
              <c> </c>
              <w xml:id="fs-mnd-0000420" n="1.1.2" lemma="apace" ana="#av">apace</w>
              <pc xml:id="fs-mnd-0000430" n="1.1.2">.</pc>
              <c> </c>
              <w xml:id="fs-mnd-0000450" n="1.1.2" lemma="four" ana="#crd">Four</w>
              <c> </c>
              <w xml:id="fs-mnd-0000470" n="1.1.2" lemma="happy" ana="#j">happy</w>
              <c> </c>
              <w xml:id="fs-mnd-0000490" n="1.1.2" lemma="day" ana="#n2">days</w>
              <c> </c>
              <w xml:id="fs-mnd-0000510" n="1.1.2" lemma="bring" ana="#vvb">bring</w>
              <c> </c>
              <w xml:id="fs-mnd-0000530" n="1.1.2" lemma="in" ana="#acp-p">in</w>
            </l>
          </sp>
          <stage xml:id="stg-0364.1" n="SD 1.2.107.1" type="exit" who="#Quince_MND #Bottom_MND #Flute_MND #Snout_MND #Snug_MND #Starveling_MND">
            <w xml:id="fs-mnd-0057740" n="SD 1.2.107.1">They</w>
            <c> </c>
            <w xml:id="fs-mnd-0057760" n="SD 1.2.107.1">exit</w>
            <pc xml:id="fs-mnd-0057770" n="SD 1.2.107.1">.</pc>
          </stage>
          <sp xml:id="sp-0012" who="#Theseus_MND">
            <speaker xml:id="spk-0012">
              <w xml:id="fs-mnd-0001840">THESEUS</w>
            </speaker>
            <l xml:id="ftln-0012" n="1.1.12" part="F">
              <w xml:id="fs-mnd-0001850" n="1.1.12" lemma="go" ana="#vvb">Go</w>
              <pc xml:id="fs-mnd-0001860" n="1.1.12">,</pc>
              <c> </c>
              <w xml:id="fs-mnd-0001880" n="1.1.12" lemma="Philostrate" ana="#n1-nn">Philostrate</w>
              <pc xml:id="fs-mnd-0001890" n="1.1.12">,</pc>
            </l>
          </sp>
          <stage xml:id="stg-0020.1" n="SD 1.1.20.1" type="entrance" who="#Egeus_MND #Hermia_MND #Lysander_MND #Demetrius_MND">
            <w xml:id="fs-mnd-0003100" n="SD 1.1.20.1">Enter</w>
            <c> </c>
            <w xml:id="fs-mnd-0003120" n="SD 1.1.20.1">Egeus</w>
            <c> </c>
            <w xml:id="fs-mnd-0003140" n="SD 1.1.20.1">and</w>
            <c> </c>
            <w xml:id="fs-mnd-0003160" n="SD 1.1.20.1">his</w>
            <c> </c>
            <w xml:id="fs-mnd-0003180" n="SD 1.1.20.1">daughter</w>
            <c> </c>
            <w xml:id="fs-mnd-0003200" n="SD 1.1.20.1">Hermia</w>
            <pc xml:id="fs-mnd-0003210" n="SD 1.1.20.1">,</pc>
            <c> </c>
            <w xml:id="fs-mnd-0003230" n="SD 1.1.20.1">and</w>
            <c> </c>
            <w xml:id="fs-mnd-0003250" n="SD 1.1.20.1">Lysander</w>
            <c> </c>
            <c> </c>
            <w xml:id="fs-mnd-0003280" n="SD 1.1.20.1">and</w>
            <c> </c>
            <w xml:id="fs-mnd-0003300" n="SD 1.1.20.1">Demetrius</w>
            <pc xml:
          </stage>
        </div>
      </div>
    </body>
  </text>
</TEI>
        """
        self.toy_cast_file = "toy_cast.xml"
        self.toy_cast_text = """
        <castList xmlns="http://www.tei-c.org/ns/1.0">
        <castGroup>
          <castGroup>
            <head>four lovers</head>
            <castItem xml:id="Hermia_MND">
              <role>
                <name>Hermia</name>
              </role>
            </castItem>
            <castItem xml:id="Lysander_MND">
              <role>
                <name>Lysander</name>
              </role>
            </castItem>
            <castItem xml:id="Helena_MND">
              <role>
                <name>Helena</name>
              </role>
            </castItem>
            <castItem xml:id="Demetrius_MND">
              <role>
                <name>Demetrius</name>
              </role>
            </castItem>
          </castGroup>
        </castGroup>
        <castGroup>
          <castItem xml:id="Theseus_MND">
            <role>
              <name>Theseus</name>
            </role>
            <roleDesc>duke of Athens</roleDesc>
          </castItem>
          <castItem xml:id="Hippolyta_MND">
            <role>
              <name>Hippolyta</name>
            </role>
            <roleDesc>queen of the Amazons</roleDesc>
          </castItem>
          <castItem xml:id="Egeus_MND">
            <role>
              <name>Egeus</name>
            </role>
            <roleDesc>father to Hermia</roleDesc>
          </castItem>
          <castItem xml:id="Philostrate_MND">
            <role>
              <name>Philostrate</name>
            </role>
            <roleDesc>master of the revels to Theseus</roleDesc>
          </castItem>
        </castGroup>
        <castGroup>
          <head>Lords and Attendants on Theseus and Hippolyta</head>
          <castItem xml:id="ATTENDANTS_MND"/>
          <castItem xml:id="ATTENDANTS.0.1_MND" corresp="#ATTENDANTS_MND"/>
          <castItem xml:id="ATTENDANTS.0.2_MND" corresp="#ATTENDANTS_MND"/>
        </castGroup>
        </castList>
        """
        with open(self.toy_xml_file, "w") as f:
            f.write(self.toy_xml_text)
        self.soup = get_soup(self.toy_xml_file)
        self.xml_df = get_xml_df(get_body(self.soup))
        with open(self.toy_cast_file, "w") as f:
            f.write(self.toy_cast_text)

    def tearDown(self) -> None:
        if os.path.exists(self.toy_xml_file):
            os.remove(self.toy_xml_file)
        if os.path.exists(self.toy_cast_file):
            os.remove(self.toy_cast_file)

    def test_get_annotated_xml_df(self):
        # TODO Test
        df = get_raw_xml_df(self.toy_xml_file)
        df

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
        self.assertTrue(has_speaker(self.xml_df.query("tag == 'sp'").iloc[0]))
        self.assertFalse(has_speaker(self.xml_df.query("tag == 'w'").iloc[0]))

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
        for idx, row in self.xml_df.query(
            "tag == 'stage' and type == 'entrance'"
        ).iterrows():
            self.assertTrue(is_entrance(row))

    def test_is_exit(self):
        for idx, row in self.xml_df.query(
            "tag == 'stage' and type == 'exit'"
        ).iterrows():
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
        set_act(self.xml_df)
        self.assertTrue(is_new_act(self.xml_df.query("tag == 'sp'").iloc[0], 0))
        self.assertFalse(is_new_act(self.xml_df.query("tag == 'sp'").iloc[0], 1))

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
        set_act(self.xml_df)
        self.assertListEqual(list(self.xml_df.query("type == 'act'")["act"]), [1])
        self.assertFalse(any(pd.isna(x) for x in self.xml_df["act"]))
        pass

    def test_set_onstage(self):
        set_act(self.xml_df)
        set_onstage(self.xml_df)
        self.assertEqual(
            self.xml_df.query("tag == 'stage'").iloc[0]["onstage"],
            "#ATTENDANTS_MND #Hippolyta_MND #Philostrate_MND #Theseus_MND",
        )

    def test_set_scene(self):
        set_scene(self.xml_df)
        self.assertTrue(set(self.xml_df.query("type == 'act'")["scene"]) == {0})
        self.assertFalse(0 in set(self.xml_df.query("type != 'act'")["scene"]))
        self.assertFalse(any(pd.isna(x) for x in self.xml_df["scene"]))

    def test_set_speaker(self):
        set_speaker(self.xml_df, get_body(self.soup))
        # TODO test on 'sp' tag once decided what the desired behavior there is
        self.assertEqual(
            self.xml_df.query("tag == 'l'").iloc[0]["speaker"], "#Theseus_MND"
        )
        self.assertEqual(
            self.xml_df[self.xml_df["xml:id"] == "ftln-0012"].iloc[0]["speaker"],
            "#Theseus_MND",
        )

    def test_set_stagegroup(self):
        # TODO test
        pass
