import os
from io import StringIO
from unittest import TestCase

import pandas as pd

from hyperbard.preprocessing import get_soup


class XMLTestCase(TestCase):
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
              <sp xml:id="sp-0012" who="#Philostrate_MND">
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
        with open(self.toy_cast_file, "w") as f:
            f.write(self.toy_cast_text)
        self.toy_agg_df = pd.read_csv(
            StringIO(
                """
act,scene,stagegroup,stagegroup_raw,setting,onstage,speaker,n_lines,n_tokens
1,1,1,1,1,#ATTENDANTS_MND #Philostrate_MND #Theseus_MND,#Theseus_MND,6,43
1,1,2,2,2,#ATTENDANTS_MND #Hippolyta_MND #Philostrate_MND #Theseus_MND,#Hippolyta_MND,5,35
1,2,3,3,3,#ATTENDANTS_MND #Demetrius_MND #Egeus_MND #Hermia_MND #Hippolyta_MND #Lysander_MND #Theseus_MND,#Egeus_MND,1,6
1,2,3,3,4,#ATTENDANTS_MND #Demetrius_MND #Egeus_MND #Hermia_MND #Hippolyta_MND #Lysander_MND #Theseus_MND,#Theseus_MND,1,8
2,1,4,4,5,#ATTENDANTS_MND #Demetrius_MND #Egeus_MND #Hermia_MND #Hippolyta_MND #Lysander_MND #Theseus_MND,#Egeus_MND,1,7
"""
            )
        )

    def tearDown(self) -> None:
        if os.path.exists(self.toy_xml_file):
            os.remove(self.toy_xml_file)
        if os.path.exists(self.toy_cast_file):
            os.remove(self.toy_cast_file)
