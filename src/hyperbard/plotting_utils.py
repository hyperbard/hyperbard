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
