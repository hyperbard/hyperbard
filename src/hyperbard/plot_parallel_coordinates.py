"""Parallel coordinate plotting script (ranking of characters)."""

import pandas as pd

from cycler import cycler
from matplotlib import cm

from hyperbard.io import load_graph
from hyperbard.ranking import get_character_ranking
from hyperbard.utils import get_name_from_identifier

import matplotlib.pyplot as plt



def plot_character_rankings(character_ranking_df, save_path=None):
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(
            3 * (len(character_ranking_df.columns) - 1),
            9 + len(character_ranking_df) // 10,
        ),
    )
    custom_cycler = cycler(linestyle=["-", "--", ":", "-."]) * cycler(
        marker=["^", ">", "v", "<"]
    )
    cmap = lambda i: cm.tab20c(i) if i % 2 == 0 else cm.tab20b(i)
    ax.set_prop_cycle(custom_cycler)
    pd.plotting.parallel_coordinates(
        character_ranking_df,
        class_column="index",
        colormap=cmap,
        ax=ax,
        alpha=0.5,
    )
    ax.invert_yaxis()
    labels = [
        get_name_from_identifier(elem.get_text()) for elem in ax.legend().get_texts()
    ]
    plt.legend(loc=(1, 0), labels=labels)
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, transparent=True, bbox_inches="tight", backend="pgf")
        plt.close()
    else:
        plt.show()


if __name__ == '__main__':

    # TODO: Make configurable; should come from iteration or outside
    # argument?
    play = 'romeo-and-juliet'

    se_scene = load_graph(play, 'se-scene-w', 'n_lines')
    se_group = load_graph(play, 'se-group-w', 'n_lines')
    se_speech = load_graph(play, 'se-speech-wd', 'n_lines')

    ce_scene_b = load_graph(play, 'ce-scene-w', 'count')
    ce_scene_m = load_graph(play, 'ce-scene-mw', 'n_lines')

    ce_group_b = load_graph(play, 'ce-group-w')
    ce_group_m = load_graph(play, 'ce-group-mw', 'n_lines')

    representations = [
        {
            'name': '01_se-scene-b',
            'graph': se_scene,
        },
        {
            'name': '02_se-scene-w',
            'graph': se_scene,
            'weight': 'n_lines',
        },
        {
            'name': '03_se-group-b',
            'graph': se_group,
        },
        {
            'name': '04_se-group-w',
            'graph': se_group,
            'weight': 'n_lines',
        },
        {
            'name': '05_se-speech-wd_in',
            'graph': se_speech,
            'weight': 'n_lines',
            'degree': 'in',
        },
        {
            'name': '06_se-speech-wd_out',
            'graph': se_speech,
            'weight': 'n_lines',
            'degree': 'out',
        },
        {
            'name': '07_ce-scene-b',
            'graph': ce_scene_b,
        },
        {
            # TODO: Is this correct?
            'name': '08_ce-scene-mb',
            'graph': ce_scene_m,
        },
        {
            'name': '09_ce-scene-mw',
            'graph': ce_scene_m,
            'weight': 'n_lines',
        },
        {
            'name': '10-ce-group-b',
            'graph': ce_group_b,
        },
        {
            'name': '11-ce-group-mb',
            'graph': ce_group_m,
        },
        {
            'name': '12-ce-group-mw',
            'graph': ce_group_m,
            'weight': 'n_lines',
        },
    ]

    df_ranking = get_character_ranking(representations)
    print(df_ranking)

    plot_character_rankings(df_ranking)
