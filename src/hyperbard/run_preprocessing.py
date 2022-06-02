import os
from glob import glob
from multiprocessing import Pool, cpu_count

from statics import DATA_PATH, RAWDATA_PATH

from hyperbard.preprocessing import (
    get_annotated_xml_df,
    get_filename_base,
    get_setting_df,
)


def handle_file(file):
    print(f"Starting {file}...")
    df = get_annotated_xml_df(file)
    df.to_csv(f"{DATA_PATH}/{get_filename_base(file)}.raw.csv", index=False)
    aggdf = get_setting_df(df)
    assert all(
        [bool(x) for x in aggdf.onstage]
    ), f"{file}: found nan values in 'onstage' column of aggregated (i.e., speech-only) dataframe!"
    aggdf.to_csv(f"{DATA_PATH}/{get_filename_base(file)}.agg.csv", index=False)


if __name__ == "__main__":
    files = sorted(glob(f"{RAWDATA_PATH}/*.xml"))
    print(f"Found {len(files)} files to process.")
    os.makedirs(DATA_PATH, exist_ok=True)

    with Pool(cpu_count() - 3) as p:
        p.map(handle_file, files)
