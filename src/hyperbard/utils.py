import regex as re


def character_string_to_sorted_list(character_string):
    return sorted(set(character_string.split()))


def split_identifier(character_string):
    return re.split("_.*?$", character_string, maxsplit=1)[0].replace("#", "")


def join_strings(list_of_strings):
    return " ".join(list_of_strings)
