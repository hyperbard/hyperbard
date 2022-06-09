import os
from collections import Counter
from glob import glob
from random import random
from time import sleep

import pandas as pd
import regex as re
import requests
from bs4 import BeautifulSoup

from hyperbard.statics import META_PATH, RAWDATA_PATH


def generate_xml_statistics(xml_counter, counted_name, files):
    dfs = dict()
    for file in files:
        with open(file) as f:
            filename = file.split("/")[-1].split("_")[0]
            soup = BeautifulSoup(f, "lxml-xml")
            dfs[filename] = pd.DataFrame(
                xml_counter(soup).most_common(), columns=[counted_name, f"c_{filename}"]
            ).set_index(counted_name)
            print("Done:", filename)
    df = pd.concat(dfs.values(), axis=1).fillna(0).astype(int)
    df["c_total"] = df.sum(axis=1)
    df = df.sort_values("c_total", ascending=False)[[df.columns[-1], *df.columns[:-1]]]
    return df


def count_paths(files):
    xml_counter = lambda soup: Counter(
        "/".join(reversed([t.name, *tuple(p.name for p in t.parents)]))
        for t in soup.descendants
        if t.name is not None
    )
    counted_name = "path"
    df = generate_xml_statistics(xml_counter, counted_name, files)
    df.to_csv(f"{META_PATH}/xml_{counted_name}_counts.csv")


def count_tags(files):
    xml_counter = lambda soup: Counter(
        t.name for t in soup.descendants if t.name is not None
    )
    counted_name = "tag"
    df = generate_xml_statistics(xml_counter, counted_name, files)
    df.to_csv(f"{META_PATH}/xml_{counted_name}_counts.csv")


def count_attributes(files):
    xml_counter = lambda soup: Counter(
        t.name + "/" + "|".join(sorted(t.attrs.keys()))
        for t in soup.descendants
        if t.name is not None
    )
    counted_name = "tag_attrs"
    df = generate_xml_statistics(xml_counter, counted_name, files)
    df.to_csv(f"{META_PATH}/xml_{counted_name}_counts.csv")


def make_tag_url(tag):
    return f"https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-{tag}.html"


def get_tag_description(tag_url):
    res = requests.get(tag_url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text)
        sleep(random())
        return soup.table.tr.td.text
    else:
        raise Exception(res)


def retrieve_tag_descriptions():
    df = pd.read_csv(f"{META_PATH}/xml_tag_counts.csv")
    df_tag_descriptions = pd.DataFrame(
        index=df.tag, columns=["url", "description"], data=""
    )
    df_tag_descriptions["url"] = df_tag_descriptions.index.map(make_tag_url)
    df_tag_descriptions["description"] = df_tag_descriptions.url.map(
        get_tag_description
    )  # this takes a bit of time b/c we are being nice to the server
    df_tag_descriptions["description"] = df_tag_descriptions.description.map(
        lambda desc: re.sub("\s+", " ", desc.strip())
    )
    df_tag_descriptions[["description", "url"]].to_csv(
        f"{META_PATH}/xml_tag_descriptions.csv"
    )


if __name__ == "__main__":
    files = sorted(glob(f"{RAWDATA_PATH}/**.xml"))
    os.makedirs(META_PATH, exist_ok=True)
    count_paths(files)
    count_tags(files)
    count_attributes(files)
    retrieve_tag_descriptions()
