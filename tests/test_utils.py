from unittest import TestCase

from hyperbard.utils import (
    character_string_to_sorted_list,
    get_name_from_identifier,
    sort_join_strings,
)


class UtilsTest(TestCase):
    def setUp(self) -> None:
        self.identifier = "#Theseus_MND"
        self.character_list = [
            "#ATTENDANTS_MND",
            "#Hippolyta_MND",
            "#Philostrate_MND",
            "#Theseus_MND",
        ]
        self.character_string_unsorted = "#Hippolyta_MND  #Demetrius_MND #Egeus_MND \
        #Hermia_MND #Lysander_MND #Theseus_MND   #ATTENDANTS_MND"

    def test_character_string_to_sorted_list(self):
        self.assertListEqual(
            character_string_to_sorted_list(self.character_string_unsorted),
            [
                "#ATTENDANTS_MND",
                "#Demetrius_MND",
                "#Egeus_MND",
                "#Hermia_MND",
                "#Hippolyta_MND",
                "#Lysander_MND",
                "#Theseus_MND",
            ],
        )

    def test_get_name_from_identifier(self):
        self.assertEqual(get_name_from_identifier(self.identifier), "Theseus")

    def test_sort_join_strings(self):
        self.assertEqual(
            sort_join_strings(self.character_list),
            "#ATTENDANTS_MND #Hippolyta_MND #Philostrate_MND #Theseus_MND",
        )
