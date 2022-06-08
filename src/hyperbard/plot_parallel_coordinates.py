"""Parallel coordinate plotting script (ranking of characters)."""

from hyperbard.io import load_graph
from hyperbard.ranking import get_character_ranking


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
