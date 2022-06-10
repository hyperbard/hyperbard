from matplotlib import cm as cm
from matplotlib import pyplot as plt


def set_rcParams(fontsize=None):
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = "Palatino"
    plt.rcParams["text.usetex"] = True
    plt.rcParams["pdf.fonttype"] = 42
    if fontsize is not None:
        plt.rcParams["font.size"] = fontsize


def save_pgf_fig(path, axis_off=False, tight=False):
    if axis_off:
        plt.axis("off")
    if tight:
        plt.tight_layout()
    plt.savefig(
        path,
        backend="pgf",
        bbox_inches="tight",
        transparent=True,
    )
    plt.close()


def get_character_color(k):
    if k == "Romeo":
        color = cm.tab10(1)
    elif k == "Juliet":
        color = cm.tab10(3)
    elif k == "Nurse":
        color = cm.tab10(2)
    elif k == "Capulet":
        color = cm.tab10(0)
    elif k == "LadyCapulet":
        color = cm.tab10(4)
    else:
        color = "k"
    return color
