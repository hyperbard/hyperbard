from typing import Union

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import NavigableString, PageElement, Tag

from hyperbard.utils import sort_join_strings


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


def who_string_to_set(who_string: Union[str, float]) -> Union[set, float]:
    return set(who_string.split()) if not pd.isna(who_string) else who_string


def set_onstage(df: pd.DataFrame) -> None:
    df["who"] = df.who.map(who_string_to_set)
    df["onstage"] = [set()] * len(df)
    for idx, row in df.iterrows():
        prev_onstage = df.at[idx - 1, "onstage"] if idx > 0 else set()
        prev_act = df.at[idx - 1, "act"] if idx > 0 else 0
        #  flush characters when new act starts
        #  necessary to limit repercussions of encoding "errors" in stage directions
        #  e.g., dead or unconscious people are not usually marked up as exiting
        #  cause of discovery: in R&J, Juliet not marked to exit at the end of Act IV
        #  not flushing after every _scene_ b/c e.g., in Julius Caesar Act IV Scene II/III,
        #  Folger Shakespeare (differing from the Oxford Version also in the text) does not
        #  have Brutus and Cassius enter Scene III separately, and there might be more
        #  instances like this
        #  flushing after every act also is problematic b/c in rare instances, characters remain across acts (see below)
        if row["act"] != prev_act:  # or row["scene"] != prev_scene:
            prev_onstage = set()
        #  register changes to characters (within the same scene) + make sure speaker is always on stage
        if (row["tag"] == "stage" and row["type"] == "entrance") or (
            row["tag"] == "sp" and not pd.isna(row["who"])
        ):
            df.at[idx, "onstage"] = prev_onstage | row["who"]
        elif row["tag"] == "stage" and row["type"] == "exit":
            df.at[idx, "onstage"] = prev_onstage - row["who"]
        else:
            df.at[idx, "onstage"] = prev_onstage
    assert not any(
        pd.isna(x) for x in df["onstage"]
    ), f"Found unexpected nan values in 'onstage' column!"
    df.onstage = df.onstage.apply(sort_join_strings)


def set_stagegroup(df: pd.DataFrame) -> None:
    df["stagegroup"] = float("nan")
    stage_n = 0
    for idx1, (os1, os2) in enumerate(zip(df.onstage[:-1], df.shift(-1).onstage)):
        if idx1 == 0:
            df.at[idx1, "stagegroup"] = stage_n
        if os1 != os2:
            stage_n += 1
        df.at[idx1 + 1, "stagegroup"] = stage_n
    df.stagegroup = df.stagegroup.astype(int)


def get_who_attributes(elem):
    # the nan is relevant for sp tags of songs without who annotations
    return elem.attrs.get("who", float("nan"))


def get_descendants_ids(elem):
    return [
        e.attrs["xml:id"]
        for e in elem.descendants
        if type(e) != NavigableString and e.attrs.get("n")
    ]


def set_speaker(df, body):
    speech_tags = body.find_all("sp")
    speaker_helper = zip(
        map(get_who_attributes, speech_tags),
        map(get_descendants_ids, speech_tags),
    )
    df["speaker"] = float("nan")
    for speaker, descendants in speaker_helper:
        df.loc[df["xml:id"].map(lambda x: x in descendants), "speaker"] = speaker
    df.speaker = df.speaker.apply(
        lambda sp: " ".join(sorted(set(sp.split()))) if not pd.isna(sp) else sp
    )


def get_annotated_xml_df(file):
    soup = get_soup(file)
    body = get_body(soup)
    df = get_xml_df(body)
    set_act(df)
    set_scene(df)
    set_onstage(df)
    set_stagegroup(df)
    set_speaker(df, body)
    return df


def get_setting_df(df):
    # speaker mentions in text have already been filtered out in a previous step
    # "n" attributes of stage directions start with SD
    aggregated = (
        df.query("tag == 'w' and not n.fillna('').str.contains('[A-Za-z]')")
        .groupby(["stagegroup", "onstage", "speaker", "n"])
        .count()[["tag"]]
        .rename(dict(tag="n_tokens"), axis=1)
        .reset_index()
    )
    aggregated["n_split"] = aggregated.n.map(
        lambda identifier: [
            int(id_part) for id_part in identifier.split()[-1].split(".")
        ]
    )
    aggregated = aggregated.sort_values("n_split").reset_index(drop=True)
    aggregated["setting"] = float("nan")
    setting_n = 1  # first non-empty stagegroup is 1, too -> consistency
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
    aggregated["act"] = aggregated.n_split.map(lambda x: x[0])
    aggregated["scene"] = aggregated.n_split.map(lambda x: x[1])
    aggregated_grouped = (
        aggregated.groupby(
            ["stagegroup", "onstage", "speaker", "setting", "act", "scene"]
        )
        .agg(dict(n_tokens="sum", n="count"))
        .reset_index()
        .rename(dict(n="n_lines"), axis=1)
        .sort_values("setting")
    )
    return aggregated_grouped.reset_index(drop=True)
