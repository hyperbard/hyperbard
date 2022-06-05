import math
from unittest import TestCase

from bs4 import BeautifulSoup

from hyperbard.preprocessing import get_attrs, get_body, get_soup


class PreprocessingTest(TestCase):
    def setUp(self) -> None:
        self.toy_xml_file = "tei_toy.xml"
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
