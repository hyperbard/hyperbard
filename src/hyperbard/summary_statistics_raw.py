"""Calculate summary statistics of pre-processed raw data."""

from glob import glob
from hyperbard.preprocessing import get_filename_base
from statics import DATA_PATH, META_PATH

import pandas as pd


if __name__ == '__main__':
    filenames_raw = sorted(glob(f"{DATA_PATH}/*.raw.csv"))
    filenames_agg = sorted(glob(f"{DATA_PATH}/*.agg.csv"))

    NAME_TO_TYPE = pd.read_csv(
        f"{META_PATH}/playtypes.csv").set_index("play_name")

    # Will contain the results of all operations of this script.
    df_out = []

    for filename_raw, filename_agg in zip(filenames_raw, filenames_agg):
        df_raw = pd.read_csv(filename_raw, low_memory=False)
        df_agg = pd.read_csv(filename_agg, low_memory=False)

        play = get_filename_base(filename_raw)
        play = play.split('_')[0]

        n_characters = len(df_raw['speaker'].dropna().unique())

        n_words = df_agg['n_tokens'].sum()
        n_lines = df_agg['n_lines'].sum()

        row = {
            'play': play,
            'n_characters': n_characters,
            'n_words': n_words,
            'n_lines': n_lines,
            'type': NAME_TO_TYPE.at[play, 'play_type'],
        }

        df_out.append(row)

    df_out = pd.DataFrame.from_records(df_out)
    print(df_out.to_csv(index=False))
