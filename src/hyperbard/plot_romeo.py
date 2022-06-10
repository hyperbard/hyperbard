from hyperbard.plot_romeo_bipartite import plot_romeo_bipartite
from hyperbard.plot_romeo_hypergraph_over_time import plot_romeo_hypergraph_over_time
from hyperbard.plot_romeo_hypergraphs import plot_romeo_hypergraphs
from hyperbard.plot_romeo_radials import (
    plot_romeo_radials_full,
    plot_romeo_radials_partial,
)
from hyperbard.plotting_utils import set_rcParams

if __name__ == "__main__":
    set_rcParams()
    height = 6
    font_size = 22

    selected_labels = sorted(["Juliet", "Romeo", "Capulet", "LadyCapulet", "Nurse"])

    # plot_romeo_radials_full(selected_labels, font_size, height)
    # plot_romeo_radials_partial(selected_labels, font_size, height)

    plot_romeo_bipartite(selected_labels, font_size)

    plot_romeo_hypergraphs()

    plot_romeo_hypergraph_over_time(selected_labels, font_size)
