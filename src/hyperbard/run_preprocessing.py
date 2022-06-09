import argparse
import functools
import os
from glob import glob
from multiprocessing import Pool, cpu_count

from statics import DATA_PATH, RAWDATA_PATH

from hyperbard.preprocessing import get_agg_xml_df, get_cast_df, get_raw_xml_df
from hyperbard.utils import get_filename_base


def handle_file(file, args):
    try:
        print(f"Starting {file}...")
        filename_base = get_filename_base(file, full=False)

        out_file = f"{DATA_PATH}/{filename_base}.cast.csv"

        if os.path.exists(out_file) and not args.force:
            print(f"{out_file} already exists; will not overwrite")
        else:
            #  .cast.csv
            cast_df = get_cast_df(file)
            cast_df.to_csv(f"{out_file}", index=False)

        out_file = f"{DATA_PATH}/{filename_base}.raw.csv"

        if os.path.exists(out_file) and not args.force:
            print(f"{out_file} already exists; will not overwrite")
        else:
            #  .raw.csv
            df = get_raw_xml_df(file)
            df.to_csv(f"{out_file}", index=False)

        out_file = f"{DATA_PATH}/{filename_base}.agg.csv"

        if os.path.exists(out_file) and not args.force:
            print(f"{out_file} already exists; will not overwrite")
        else:
            aggdf = get_agg_xml_df(df)
            assert all(
                [bool(x) for x in aggdf.onstage]
            ), f"{file}: found nan values in 'onstage' column of aggregated (i.e., speech-only) dataframe!"

            # .agg.csv
            aggdf.to_csv(f"{out_file}", index=False)

    except TypeError as e:
        raise Exception(f"Problem with {file}: {e}")


if __name__ == "__main__":
    files = sorted(glob(f"{RAWDATA_PATH}/*.xml"))
    print(f"Found {len(files)} files to process.")
    os.makedirs(DATA_PATH, exist_ok=True)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--force", action="store_true", help="If set, overwrites files"
    )

    args = parser.parse_args()

    with Pool(cpu_count() - 3) as p:
        file_handler = functools.partial(
            handle_file,
            args=args
        )
        p.map(file_handler, files)
