"""Calculate summary statistics of pre-processed raw data."""

from glob import glob

import pandas as pd
from statics import DATA_PATH, META_PATH

from hyperbard.utils import get_filename_base, string_to_set


def compute_raw_statistics(filename_agg: str, name_to_type: pd.DataFrame) -> dict:
    play = get_filename_base(filename_agg, full=True).split(".")[0]
    df_agg = pd.read_csv(filename_agg, low_memory=False)

    speaking_characters = {
        elem for subset in df_agg.speaker.map(string_to_set) for elem in subset
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


def compute_all_raw_statistics(filenames_agg, name_to_type):
    rows = []

    for filename_agg in filenames_agg:
        row = compute_raw_statistics(filename_agg, name_to_type)
        rows.append(row)

    return pd.DataFrame.from_records(rows)


if __name__ == "__main__":
    filenames_agg = sorted(glob(f"{DATA_PATH}/*.agg.csv"))
    name_to_type = pd.read_csv(f"{META_PATH}/playtypes.csv", comment='#').set_index("play_name")
    df = compute_all_raw_statistics(filenames_agg, name_to_type)
    df.to_csv(f"{META_PATH}/summary_statistics_raw.csv", index=False)
    #  print(df.to_csv(index=False))
