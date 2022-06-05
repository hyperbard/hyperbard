"""Calculate summary statistics of pre-processed raw data."""

from glob import glob

import pandas as pd
from statics import DATA_PATH, META_PATH

from hyperbard.utils import get_filename_base


def compute_raw_statistics(
    filename_cast: str, filename_agg: str, name_to_type: pd.DataFrame
) -> dict:
    play = get_filename_base(filename_cast, full=True).split(".")[0]
    assert (
        play == get_filename_base(filename_agg, full=True).split(".")[0]
    ), f"Filenames don't match - raw: {filename_cast}, agg: {filename_agg} - check your data!"

    df_cast = pd.read_csv(filename_cast, low_memory=False)
    df_agg = pd.read_csv(filename_agg, low_memory=False)

    n_characters = len(df_cast)
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
    filenames_cast = sorted(glob(f"{DATA_PATH}/*.cast.csv"))
    filenames_agg = sorted(glob(f"{DATA_PATH}/*.agg.csv"))
    name_to_type = pd.read_csv(f"{META_PATH}/playtypes.csv").set_index("play_name")
    df = compute_all_raw_statistics(filenames_cast, filenames_agg, name_to_type)
    df.to_csv(f"{META_PATH}/summary_statistics_raw.csv", index=False)
    #  print(df.to_csv(index=False))
