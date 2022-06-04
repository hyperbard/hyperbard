"""Calculate summary statistics of pre-processed raw data."""

from glob import glob

import pandas as pd
from statics import DATA_PATH, META_PATH

from hyperbard.preprocessing import get_filename_base


def compute_raw_statistics(
    filename_raw: str, filename_agg: str, name_to_type: pd.DataFrame
) -> dict:
    play = get_filename_base(filename_raw, full=False)
    assert play == get_filename_base(
        filename_agg, full=False
    ), f"Filenames don't match - raw: {filename_raw}, agg: {filename_agg} - check your data!"

    df_raw = pd.read_csv(filename_raw, low_memory=False)
    df_agg = pd.read_csv(filename_agg, low_memory=False)

    # TODO fix
    # this currently counts unique characters that speak ("active characters")
    # - undercounting: characters that do not speak
    # fix could look at other part of raw data (currently thrown away)
    speaking_characters = {
        item
        for sublist in df_raw.speaker.dropna().map(lambda x: x.split())
        for item in sublist
    }
    n_characters = len(speaking_characters)

    n_words = df_agg["n_tokens"].sum()
    n_lines = df_agg["n_lines"].sum()

    row = {
        "play": play,
        "n_characters": n_characters,
        "n_words": n_words,
        "n_lines": n_lines,
        "type": name_to_type.at[play, "play_type"],
    }
    return row


def compute_all_raw_statistics(filenames_raw, filenames_agg, name_to_type):
    rows = []

    for filename_raw, filename_agg in zip(filenames_raw, filenames_agg):
        row = compute_raw_statistics(filename_raw, filename_agg, name_to_type)
        rows.append(row)

    return pd.DataFrame.from_records(rows)


if __name__ == "__main__":
    filenames_raw = sorted(glob(f"{DATA_PATH}/*.raw.csv"))
    filenames_agg = sorted(glob(f"{DATA_PATH}/*.agg.csv"))
    name_to_type = pd.read_csv(f"{META_PATH}/playtypes.csv").set_index("play_name")
    df = compute_all_raw_statistics(filenames_raw, filenames_agg, name_to_type)
    df.to_csv(f"{META_PATH}/summary_statistics_raw.csv", index=False)
    # print(df.to_csv(index=False))
