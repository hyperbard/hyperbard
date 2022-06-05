import math
from unittest import TestCase

from bs4 import BeautifulSoup

from hyperbard.preprocessing import get_attrs, get_body, get_soup


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
            <pc xml:id="fs-mnd-0003310" n="SD 1.1.20.1">.</pc>
          </stage>
        </div>
      </div>
    </body>
  </text>
</TEI>
        """
        with open(self.toy_xml_file, "w") as f:
            f.write(self.toy_xml_text)
        self.soup = get_soup(self.toy_xml_file)

    def test_get_soup(self):
        self.assertTrue(bool(self.soup.text))
        self.assertEqual(self.soup.find_all("w")[-1].get_text(), "Demetrius")

    def test_get_body(self):
        body = get_body(self.soup)
        self.assertEqual(body.parent.name, "text")
        self.assertEqual(body.find_all("w")[0].get_text(), "ACT")

    def test_get_attrs(self):
        elem_notext = self.soup.find("div")
        attrs_notext = get_attrs(elem_notext)
        self.assertTrue(math.isnan(attrs_notext["text"]))
        del attrs_notext["text"]
        self.assertEqual(
            attrs_notext,
            {"tag": "div", "type": "act", "n": "1"},
        )
        elem_text = self.soup.find("w")
        attrs_text = get_attrs(elem_text)
        self.assertEqual(
            attrs_text,
            {"tag": "w", "xml:id": "fs-mnd-0000010", "text": "ACT"},
        )
