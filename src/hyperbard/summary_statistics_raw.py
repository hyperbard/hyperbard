"""Calculate summary statistics of pre-processed raw data."""

from glob import glob
from hyperbard.preprocessing import get_filename_base
from statics import DATA_PATH

import pandas as pd



if __name__ == '__main__':
    filenames = sorted(glob(f"{DATA_PATH}/*.raw.csv"))

    # Will contain the results of all operations of this script.
    df_out = []

    for filename in filenames:
        df = pd.read_csv(filename, low_memory=False)
        play = get_filename_base(filename)
        play = play.split('_')[0]

        n_characters = len(df['speaker'].dropna().unique())
        n_words = len(df[df['tag'] == 'w'])

        row = {
            'play': play,
            'n_characters': n_characters,
            'n_words': n_words,
        }

        df_out.append(row)

    df_out = pd.DataFrame.from_records(df_out)
    print(df_out)
