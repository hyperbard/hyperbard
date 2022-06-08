"""Parallel coordinate plotting script (ranking of characters)."""

from hyperbard.io import load_graph
from hyperbard.ranking import get_character_ranking


if __name__ == '__main__':

    # TODO: Make configurable; should come from iteration or outside
    # argument?
    play = 'romeo-and-juliet'

    se_scene = load_graph(play, 'se-scene-w', 'n_lines')
    se_group = load_graph(play, 'se-group-w', 'n_lines')

    #ce_scene_b = load_graph(play, 'ce-scene-mw')
    #ce_scene_mb = load_graph(play, 'ce-scene-w', 'count')
    #ce_scene_mw = load_graph(play, 'ce-scene-mw', 'n_lines')

    #ce_group_b = load_graph(play, 'ce-group-mw')
    #ce_group_mb = load_graph(play, 'ce-group-w', 'count')
    #ce_group_mw = load_graph(play, 'ce-group-mw', 'n_lines')

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
            'name': '02_se-group-w',
            'graph': se_group,
            'weight': 'n_lines',
        },
    ]

    df_ranking = get_character_ranking(representations)
    print(df_ranking)
