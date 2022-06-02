import os

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import NavigableString


def get_filename_base(file):
    return os.path.splitext(os.path.split(file)[-1])[0]


def get_soup(file, parser="lxml-xml"):
    with open(file) as f:
        soup = BeautifulSoup(f, parser)
    return soup


def get_body(soup):
    texts = soup.find_all("text")
    assert len(texts) == 1, "Found multiple text tags, expected exactly one."
    text = texts[0]
    bodies = text.find_all("body")
    assert len(bodies) == 1, "Found no body tag in text, expected exactly one."
    return bodies[0]


def get_attrs(elem):
    if len(elem.contents) <= 1:
        return {"tag": elem.name, **elem.attrs, "text": elem.text}
    else:
        return {"tag": elem.name, **elem.attrs, "text": float("nan")}


def get_xml_df(body):
    return pd.DataFrame.from_records(
        [
            get_attrs(elem)
            for elem in body.descendants
            if type(elem) != NavigableString
            and elem.name not in ["head", "speaker"]
            and not {"head", "speaker"}.intersection(
                set([x.name for x in elem.parents])
            )  # filters out head and speaker words as info already in div attributes
        ]
    )


def set_act(df):
    df["act"] = float("nan")
    df.loc[df.query("type == 'act'").index, "act"] = df.query("type == 'act'")["n"]
    df["act"] = df.act.ffill().bfill().astype(int)


def set_scene(df):
    df["scene"] = float("nan")
    df.loc[df.query("type == 'act'").index, "scene"] = 0
    df.loc[df.query("type == 'scene'").index, "scene"] = df.query("type == 'scene'")[
        "n"
    ]
    df["scene"] = df.scene.ffill().bfill().astype(int)


def set_onstage(df):
    df["who"] = df.who.map(
        lambda who_string: set(who_string.split())
        if not pd.isna(who_string)
        else who_string
    )
    df["onstage"] = [set()] * len(df)
    for idx, row in df.iterrows():
        prev_onstage = df.at[idx - 1, "onstage"] if idx > 0 else set()
        prev_act = df.at[idx - 1, "act"] if idx > 0 else 0
        prev_scene = df.at[idx - 1, "scene"] if idx > 0 else 0
        #  flush characters when new act starts
        #  necessary to limit repercussions of encoding "errors" in stage directions
        #  e.g., dead or unconscious people are not usually marked up as exiting
        #  cause of discovery: in R&J, Juliet not marked to exit at the end of Act IV
        #  not flushing after every _scene_ b/c e.g., in Julius Caesar Act IV Scene II/III,
        #  Folger Shakespeare (differing from the Oxford Version also in the text) does not
        #  have Brutus and Cassius enter Scene III separately, and there might be more
        #  instances like this
        if row["act"] != prev_act:  # or row["scene"] != prev_scene:
            prev_onstage = set()
        #  register changes to characters (within the same scene) + make sure speaker is always on stage
        if (row["tag"] == "stage" and row["type"] == "entrance") or (
            row["tag"] == "sp" and row["who"]
        ):
            df.at[idx, "onstage"] = prev_onstage | row["who"]
        elif row["tag"] == "stage" and row["type"] == "exit":
            df.at[idx, "onstage"] = prev_onstage - row["who"]
        else:
            df.at[idx, "onstage"] = prev_onstage if idx >= 1 else df.at[idx, "onstage"]
    df.onstage = df.onstage.apply(
        lambda x: " ".join(sorted(x)) if not pd.isna(x) else x
    )


def set_stagegroup(df):
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


def set_speaker(df, soup):
    speech_tags = soup.find_all("sp")
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
    set_speaker(df, soup)
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
