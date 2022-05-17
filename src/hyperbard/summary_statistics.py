"""Simple summary statistics for hypergraphs."""

import argparse

import hypernetx as hnx
import pandas as pd


def build_hypergraphs(df, level):
    """Build hypergraphs) of specified level and return them."""
    if level == 1:
        edges = []
        for (act, scene), group in df.groupby(["act", "scene", "onstage"]).agg(dict(n_tokens="sum")).reset_index().groupby(["act","scene"]):
            joined_group = tuple(sorted(set(" ".join(group.onstage).split())))
            edges.append(joined_group)
    
        H = hnx.Hypergraph(edges)
        return {'full': H}

    elif level == 2:
         df_grouped = df.groupby(["stagegroup", "onstage", "act", "scene"]).agg({"n_tokens":"sum"}).reset_index()
         df_grouped.onstage = df_grouped.onstage.map(lambda x: tuple(x.split()))
        
         Hs = {(act,scene): hnx.Hypergraph(dict(df_grouped.query("act == @act and scene == @scene").onstage))
              for (act,scene) in set(zip(df.act, df.scene))}

         return Hs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l', '--level',
        type=int,
        default=1,
        # TODO: Need to decide on a proper hierarchy here. Higher values
        # are more granular.
        help='Specifies granularity level of hypergraph to build.'
    )
    parser.add_argument(
        'INPUT',
        nargs='+',
        type=str,
        help='Input filename(s)'
    )

    args = parser.parse_args()

    for file in args.INPUT:
        df = pd.read_csv(file)
        hypergraphs = build_hypergraphs(df, args.level)

        print(hypergraphs)

