import os
from glob import glob
from multiprocessing import Pool, cpu_count

from preprocessing import get_agg_xml_df, get_raw_xml_df
from statics import DATA_PATH, RAWDATA_PATH
from utils import get_filename_base


def handle_file(file):
    print(f"Starting {file}...")
    df = get_raw_xml_df(file)
    filename_base = get_filename_base(file, full=False)
    df.to_csv(f"{DATA_PATH}/{filename_base}.raw.csv", index=False)
    aggdf = get_agg_xml_df(df)
    assert all(
        [bool(x) for x in aggdf.onstage]
    ), f"{file}: found nan values in 'onstage' column of aggregated (i.e., speech-only) dataframe!"
    aggdf.to_csv(f"{DATA_PATH}/{filename_base}.agg.csv", index=False)


if __name__ == "__main__":
    files = sorted(glob(f"{RAWDATA_PATH}/*.xml"))
    print(f"Found {len(files)} files to process.")
    os.makedirs(DATA_PATH, exist_ok=True)

    # for file in files:
    #     handle_file(file)
    with Pool(cpu_count() - 3) as p:
        p.map(handle_file, files)
