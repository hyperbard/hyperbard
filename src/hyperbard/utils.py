"""Utility functions for creating hypergraphs."""

import hypernetx as hnx


# TODO: It might make sense to refactor this according to the different
# axes/coordinates we can define (x, y, z).
def build_hypergraphs(df, level):
    """Build hypergraphs of specified level and return them."""
    if level == 1:
        edges = []
        for (act, scene), group in (
            df.groupby(["act", "scene", "onstage"])
            .agg(dict(n_tokens="sum"))
            .reset_index()
            .groupby(["act", "scene"])
        ):
            joined_group = tuple(sorted(set(" ".join(group.onstage).split())))
            edges.append(joined_group)

        H = hnx.Hypergraph(edges)
        return {"full": H}

    elif level == 2:
        df_grouped = (
            df.groupby(["stagegroup", "onstage", "act", "scene"])
            .agg({"n_tokens": "sum"})
            .reset_index()
        )
        df_grouped.onstage = df_grouped.onstage.map(lambda x: tuple(x.split()))

        Hs = {
            (act, scene): hnx.Hypergraph(
                dict(df_grouped.query("act == @act and scene == @scene").onstage)
            )
            for (act, scene) in set(zip(df.act, df.scene))
        }

        return Hs

