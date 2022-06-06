from typing import List, Union

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import NavigableString, PageElement, Tag

from hyperbard.utils import (
    character_string_to_sorted_list,
    sort_join_strings,
    string_to_set,
)


def get_soup(file: str, parser: str = "lxml-xml") -> BeautifulSoup:
    """
    Parse an XML or HTML document with the specified BeautifulSoup parser.

    :param file: Path to file
    :param parser: Parser to use
    :return: BeautifulSoup object containing the parsed file
    """
    with open(file) as f:
        soup = BeautifulSoup(f, parser)
    return soup


def get_cast_df(file: str) -> pd.DataFrame:
    soup = get_soup(file)
    cast_items = [item.attrs for item in soup.find_all("castItem")]
    cast_df = (
        pd.DataFrame.from_records(cast_items)
        .sort_values("xml:id")
        .reset_index(drop=True)
    )
    return cast_df


def get_body(soup: BeautifulSoup) -> Tag:
    """
    Extract the text body from an appropriately shaped BeautifulSoup object.

    :param soup: BeautifulSoup with exactly one text.body object
    :return: The text body as a BeautifulSoup object
    """
    texts = soup.find_all("text")
    assert len(texts) == 1, "Found multiple text tags, expected exactly one."
    text = texts[0]
    bodies = text.find_all("body")
    assert len(bodies) == 1, "Found no body tag in text, expected exactly one."
    return bodies[0]


def is_leaf(elem: Tag) -> bool:
    """
    Check if a bs4 Tag element has at most one child, i.e., if it is a leaf in the Tag tree
    (single children are NavigableStrings)

    :param elem: bs4 Tag element
    :return: If the element has at most one child
    """
    return len(elem.contents) <= 1


def get_attrs(elem: Tag) -> dict:
    """
    Get the attributes of a bs4 Tag element, plus its tag name and - if the element is a leaf - its text,
    as a dictionary.

    :param elem: bs4 Tag element
    :return: Dictionary containing the element's tag name, attributes, and - if the element is a leaf - text
    """
    if is_leaf(elem):
        return {"tag": elem.name, **elem.attrs, "text": elem.text}
    else:
        return {"tag": elem.name, **elem.attrs, "text": float("nan")}


def is_navigable_string(elem: PageElement) -> bool:
    return type(elem) == NavigableString


def is_redundant_element(elem: Union[Tag, NavigableString]) -> bool:
    """
    Check if an element is redundant, i.e., it is (contained in) a "header" or
    a "speaker" element, because the information contained in "head" and "speaker" elements
    and their descendants is already encoded in XML attributes of other tags.

    :param elem: bs4 element
    :return: If the element is redundant
    """
    return elem.name in ["head", "speaker"]


def is_descendant_of_redundant_element(elem: Union[Tag, NavigableString]) -> bool:
    parent_names = set([x.name for x in elem.parents])
    return bool({"head", "speaker"}.intersection(parent_names))


def keep_elem_in_xml_df(elem: Union[Tag, NavigableString]) -> bool:
    """
    Decide whether to keep an bs4 element in the XML dataframe produced as the
    raw preprocessed data.

    :param elem: bs4 element from a BeautifulSoup object
    :return: Whether to keep the element
    """
    return (
        not is_navigable_string(elem)
        and not is_redundant_element(elem)
        and not is_descendant_of_redundant_element(elem)
    )


def get_xml_df(body: Tag) -> pd.DataFrame:
    """
    Construct a pd.DataFrame from the non-redundant XML tags of a TEI-encoded
    BeautifulSoup object.

    :param body: Body of a TEI-encoded BeautifulSoup object
    :return: pd.DataFrame containing all non-redundant XML tags with names, attributes, and text
    """
    records = [
        get_attrs(elem) for elem in body.descendants if keep_elem_in_xml_df(elem)
    ]
    return pd.DataFrame.from_records(records)


def set_act(df: pd.DataFrame) -> None:
    """
    Adds act information to a pd.DataFrame created with get_xml_df, using the
    observation that rows with type == "act" hold the new act number in column "n".
    Complete via first forward-filling, then backward-filling,
    and convert act numbers to integers.
    Inductions, prologues, and epilogues receive special treatment as act 0
    (inductions and prologues) resp. act 6 (epilogues).

    :param df: pd.DataFrame created with get_xml_df
    :return: None
    """
    df["act"] = float("nan")
    act_query = "type == 'act'"
    df.loc[df.query(act_query).index, "act"] = df.query(act_query)["n"]
    induction_query = "type == 'induction' or type == 'prologue'"
    df.loc[df.query(induction_query).index, "act"] = 0
    epilogue_query = "type == 'epilogue'"
    df.loc[df.query(epilogue_query).index, "act"] = 6
    df["act"] = df["act"].ffill().bfill().astype(int)


def set_scene(df: pd.DataFrame) -> None:
    """
    Adds scene information to a pd.DataFrame created with get_xml_df, using the
    observation that rows with type == "scene" hold the new scene number in column "n".
    Complete via first forward-filling, then backward-filling,
    and convert act numbers to integers.
    Acts, inductions, prologues, and epilogues receive special treatment as scene 0.

    :param df: pd.DataFrame created with get_xml_df
    :return: None
    """
    df["scene"] = float("nan")
    special_types = ["act", "induction", "prologue", "epilogue"]
    general_act_query = "type in @special_types"
    df.loc[df.query(general_act_query).index, "scene"] = 0
    df.loc[df.query("type == 'scene'").index, "scene"] = df.query("type == 'scene'")[
        "n"
    ]
    df["scene"] = df.scene.ffill().bfill().astype(int)


def is_entrance(row):
    return row["tag"] == "stage" and row["type"] == "entrance"


def is_exit(row):
    return row["tag"] == "stage" and row["type"] == "exit"


def has_speaker(row):
    return row["tag"] == "sp" and not pd.isna(row["who"])


def is_new_act(row, prev_act):
    return row["act"] != prev_act


def is_new_scene(row, prev_scene):
    return row["scene"] != prev_scene


def set_onstage(df: pd.DataFrame) -> None:
    """
    Adds information on who is onstage to a pd.DataFrame created with get_xml_df,
    primarily based on hints in the XML attributes of "stage" and "sp" tags.

    Notes:

    - We ensure that the speaker(s) are always onstage.
      Note that there can be multiple speakers for one line, hence the need to treat
      the "who" attribute as a set.
    - We flush characters when a new act starts.
      Rationale: Limit repercussions of encoding "errors" in stage directions,
      found, e.g., when characters are dead or unconscious and not marked as exiting.
      Example: R&J - Juliet not marked up as exiting at the end of Act IV
    - We _also_ flush characters when a new scene starts.
      Rationale: The same as for flushing when a new act starts, but somewhat more problematic.
      Example: R&J - Citizen from Act III, Scene I never marked up as exiting,
      and thus still onstage in Act III, Scene V (on the balcony!).
    - Thus, we currently model character presence on stage "conservatively" overall, and
      we are looking into better character management (not relying on the markup)
      as a potential improvement.
    - Flushing when a new scene starts is problematic:
      Stage directions in the Folger Shakespeare often use "Exeunt all but",
      and as a consequence, only exits are marked up and not entries in the next scene.
      Example: Julius Caesar - Brutus and Cassius not marked up to enter in Act IV Scene III,
      but rather staying from Act IV Scene II (stage directions differ from the Oxford Shakespeare).
    - Even flushing when a new act starts is problematic with the Folger stage directions,
      but the problematic instances are very rare. We limit the impact of errors introduced
      by this modeling choice by also ensuring that the speaker is always onstage.

    :param df: pd.DataFrame created with get_xml_df, with act and scene already annotated
    :return: None
    """
    df["who"] = df.who.map(string_to_set)
    df["onstage"] = [set()] * len(df)
    for idx, row in df.iterrows():
        prev_onstage = df.at[idx - 1, "onstage"] if idx > 0 else set()
        prev_act = df.at[idx - 1, "act"] if idx > 0 else 0
        prev_scene = df.at[idx - 1, "scene"] if idx > 0 else 0
        if is_new_act(row, prev_act) or is_new_scene(row, prev_scene):
            prev_onstage = set()
        if is_entrance(row) or has_speaker(row):
            df.at[idx, "onstage"] = prev_onstage | row["who"]
        elif is_exit(row):
            df.at[idx, "onstage"] = prev_onstage - row["who"]
        else:
            df.at[idx, "onstage"] = prev_onstage
    assert not any(
        pd.isna(x) for x in df["onstage"]
    ), f"Found unexpected nan values in 'onstage' column!"
    df.onstage = df.onstage.apply(sort_join_strings)


def set_stagegroup(df: pd.DataFrame) -> None:
    df["stagegroup_raw"] = float("nan")
    stage_n = 0
    for idx1, (os1, os2) in enumerate(zip(df.onstage[:-1], df.shift(-1).onstage)):
        if idx1 == 0:
            df.at[idx1, "stagegroup_raw"] = stage_n
        if os1 != os2:
            stage_n += 1
        df.at[idx1 + 1, "stagegroup_raw"] = stage_n
    df.stagegroup_raw = df.stagegroup_raw.astype(int)


def get_who_attributes(elem: Tag) -> Union[str, float]:
    # the nan is relevant for sp tags of songs without who annotations
    return elem.attrs.get("who", float("nan"))


def get_descendants_ids(elem: Tag) -> List[str]:
    descendants = [e for e in elem.descendants if not is_navigable_string(e)]
    descendants_ids = [e.attrs["xml:id"] for e in descendants if e.attrs.get("n")]
    return descendants_ids


def set_speaker(df: pd.DataFrame, body: Tag) -> None:
    speech_tags = body.find_all("sp")
    speaker_helper = zip(
        map(get_who_attributes, speech_tags),
        map(get_descendants_ids, speech_tags),
    )
    df["speaker"] = float("nan")
    for speaker, descendants in speaker_helper:
        df.loc[df["xml:id"].map(lambda x: x in descendants), "speaker"] = speaker
    df.loc[df.query("tag == 'sp'").index, "speaker"] = df.query("tag == 'sp'")[
        "who"
    ].map(lambda val: sort_join_strings(val) if not pd.isna(val) else val)
    df.speaker = df.speaker.apply(
        lambda sp: sort_join_strings(character_string_to_sorted_list(sp))
        if not pd.isna(sp)
        else sp
    )


def get_raw_xml_df(file: str) -> pd.DataFrame:
    """
    Construct and enrich a pd.DataFrame from the non-redundant XML tags of a
    TEI-encoded BeautifulSoup object.

    Produces a DataFrame object of the shape of the *.raw.csv files.

    :param file: Path to file
    :return: pd.DataFrame containing all non-redundant XML tags with names, attributes, text, and annotations
    """
    soup = get_soup(file)
    body = get_body(soup)
    df = get_xml_df(body)
    set_act(df)
    set_scene(df)
    set_onstage(df)
    set_stagegroup(df)
    set_speaker(df, body)
    return df


def get_aggregated(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a pd.DataFrame output by get_raw_xml_df, produce a pd.DataFrame
    containing only spoken words, aggregated by speech acts, i.e., consecutive
    settings with the same speaker and the same other characters on stage.

    :param df: pd.DataFrame output by get_raw_xml_df
    :return: pd.DataFrame containing only spoken words, aggregated by speech acts
    """
    # select all words (w) that are not stage directions (SD)
    selector = "tag == 'w' and not n.fillna('').str.startswith('SD')"
    groupby = ["act", "scene", "stagegroup_raw", "onstage", "speaker", "n"]
    aggregated = (
        df.query(selector)
        .groupby(groupby)
        .agg({"tag": "count", "xml:id": "min"})
        .rename(dict(tag="n_tokens"), axis=1)
        .reset_index()
    )
    return aggregated.sort_values("xml:id").reset_index(drop=True)


def set_setting(aggregated):
    aggregated["setting"] = float("nan")
    setting_n = 1  # first non-empty stagegroup_raw is 1, too -> consistency
    aggregated.at[0, "setting"] = setting_n
    for idx, (os1, s1, os2, s2) in enumerate(
        zip(
            aggregated.onstage[:-1],
            aggregated.speaker[:-1],
            aggregated.shift(-1).onstage,
            aggregated.shift(-1).speaker[:-1],
        )
    ):
        if os1 != os2 or s1 != s2:
            setting_n += 1
        aggregated.at[idx + 1, "setting"] = setting_n
    aggregated.setting = aggregated.setting.astype(int)


def get_grouped_df(aggregated):
    aggregated_grouped = (
        aggregated.groupby(
            ["stagegroup_raw", "onstage", "speaker", "setting", "act", "scene"]
        )
        .agg(dict(n_tokens="sum", n="count"))
        .reset_index()
        .rename(dict(n="n_lines"), axis=1)
        .sort_values("setting")
    )
    stagegroups_renumbered = {
        elem: idx
        for idx, elem in enumerate(
            sorted(aggregated_grouped.stagegroup_raw.unique()), start=1
        )
    }
    aggregated_grouped["stagegroup"] = aggregated_grouped.stagegroup_raw.map(
        lambda sg: stagegroups_renumbered[sg]
    )
    columns_ordered = [
        "act",
        "scene",
        "stagegroup",
        "stagegroup_raw",
        "setting",
        "onstage",
        "speaker",
        "n_lines",
        "n_tokens",
    ]
    return aggregated_grouped[columns_ordered].reset_index(drop=True)


def get_agg_xml_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a pd.DataFrame output by get_raw_xml_df, produce a pd.DataFrame
    containing only spoken words, aggregated by speech acts, i.e., consecutive
    settings with the same speaker and the same other characters on stage,
    with full setting annotations.

    Produces a DataFrame object of the shape of the *.agg.csv files.

    :param df: pd.DataFrame output by get_raw_xml_df
    :return: pd.DataFrame containing only spoken words, aggregated by speech acts
    """
    aggregated = get_aggregated(df)
    set_setting(aggregated)
    aggregated_grouped = get_grouped_df(aggregated)
    return aggregated_grouped
