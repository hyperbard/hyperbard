from typing import Iterable, List

import regex as re


def character_string_to_sorted_list(character_string: str) -> List[str]:
    """
    Given a string of character identifiers of shape "id1 id2  id3 ... id1 idn",
    return a sorted, deduplicated list of these identifiers.

    :param character_string: String of character identifiers separated by whitespace
    :return: Sorted list of unique character identifiers
    """
    return sorted(set(re.split("\s+", character_string)))


def get_name_from_identifier(character_identifier: str) -> str:
    """
    Given a character identifier of shape "#CharacterName_PlayAbbreviation",
    extract CharacterName.

    :param character_identifier: Character identifier of shape "#CharacterName_PlayAbbreviation"
    :return: Character name
    """
    return re.split("_.*?$", character_identifier, maxsplit=1)[0].replace("#", "")


def sort_join_strings(string_iterable: Iterable[str]) -> str:
    """
    Sort and concatenate an iterable of strings, joining on a whitespace character.

    :param string_iterable: Iterable of strings (e.g., a list or a set)
    :return: String with the entries in the iterable sorted and concatenated with a whitespace as the join character
    """
    return " ".join(sorted(string_iterable))
