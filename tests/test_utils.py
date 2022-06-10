import math
from unittest import TestCase

from hyperbard.utils import (
    character_string_to_sorted_list,
    get_filename_base,
    get_name_from_identifier,
    remove_hashtag,
    remove_play_abbreviation,
    remove_uppercase_prefixes,
    sort_join_strings,
    string_to_set,
)


class UtilsTest(TestCase):
    def setUp(self) -> None:
        self.identifier = "#Theseus_MND"
        self.identifier1 = "#ATTENDANTS.0.1_MND"
        self.identifier2 = "#FAIRIES.TITANIA.Peaseblossom_MND"
        self.identifier3 = "#SERVANTS.HOTSPUR.1_1H4"
        self.identifier4 = "#TRAVELERS.CARRIERS.X_1H4"
        self.identifier5 = "#SERVANTS.GARDENER.1_R2"
        self.character_list = [
            "#ATTENDANTS_MND",
            "#Hippolyta_MND",
            "#Philostrate_MND",
            "#Theseus_MND",
        ]
        self.character_string_unsorted = "#Hippolyta_MND  #Demetrius_MND #Egeus_MND \
        #Hermia_MND #Lysander_MND #Theseus_MND   #ATTENDANTS_MND"
        self.full_filename = (
            "some/directory/a-midsummer-nights-dream_TEIsimple_FolgerShakespeare.xml"
        )

    def test_remove_hashtag(self):
        self.assertEqual(remove_hashtag(self.identifier1), "ATTENDANTS.0.1_MND")

    def test_remove_play_abbreviation(self):
        self.assertEqual(remove_play_abbreviation(self.identifier1), "#ATTENDANTS.0.1")

    def test_remove_uppercase_prefix(self):
        self.assertEqual(remove_uppercase_prefixes(self.identifier1), "ATTENDANTS.0.1")
        self.assertEqual(remove_uppercase_prefixes(self.identifier2), "Peaseblossom")
        self.assertEqual(
            remove_uppercase_prefixes(self.identifier3), "SERVANTS.HOTSPUR.1"
        )
        self.assertEqual(
            remove_uppercase_prefixes(self.identifier4), "TRAVELERS.CARRIERS.X"
        )
        self.assertEqual(
            remove_uppercase_prefixes(self.identifier5), "SERVANTS.GARDENER.1"
        )

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

    def test_get_filename_base(self):
        self.assertEqual(
            get_filename_base(
                self.full_filename,
                full=False,
            ),
            "a-midsummer-nights-dream",
        )
        self.assertEqual(
            get_filename_base(
                self.full_filename,
                full=True,
            ),
            "a-midsummer-nights-dream_TEIsimple_FolgerShakespeare",
        )

    def test_get_name_from_identifier(self):
        self.assertEqual(get_name_from_identifier(self.identifier), "Theseus")

    def test_sort_join_strings(self):
        self.assertEqual(
            sort_join_strings(self.character_list),
            "#ATTENDANTS_MND #Hippolyta_MND #Philostrate_MND #Theseus_MND",
        )

    def test_string_to_set(self):
        who_string_nonan = "#A #B #A"
        who_string_nan = float("nan")
        self.assertEqual(string_to_set(who_string_nonan), {"#A", "#B"})
        self.assertTrue(math.isnan(string_to_set(who_string_nan)))
