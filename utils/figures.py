import os

import matplotlib.pyplot as plt


def open_figure(my_dpi=96, size=800, **kwargs) -> (plt.Figure, plt.Axes):
    """
    Opens a new figure
    :param my_dpi: DPI of the figure
    :param size: Size of the figure
    :param kwargs: Any kwargs passed onto matplotlib
    :return:
    """
    fig = plt.figure(figsize=(size / my_dpi, size / my_dpi), dpi=my_dpi, **kwargs)
    axis = fig.add_subplot(111)
    return fig, axis


def save_figure(fig: plt.figure, filename, size: tuple = (30, 30), dpi=600, **kwargs):
    """
    Saves as figure to file. Creates directory if necessary. Figure size given in cm.
    :param fig: Figure object
    :param filename: Filename
    :param size: length and width in cm
    :param dpi: DPI of the resulting graphic
    :param kwargs: formats for file extensions as list, defaults to saving as png, pdf and svg
    :return: None
    """
    filename = str(filename)
    cm = 1 / 2.54
    x = size[0] * cm
    y = size[1] * cm
    fig.set_size_inches(x, y, forward=True)
    fig_path = os.path.split(filename)[0]
    if not os.path.exists(fig_path):
        os.makedirs(fig_path)
    if kwargs.get("formats"):
        for f in kwargs.pop("formats"):
            fig.savefig(f"{filename}.{f}", dpi=dpi, **kwargs)
        return
    fig.savefig(filename + ".svg", dpi=dpi, **kwargs)
    fig.savefig(filename + ".png", dpi=dpi, **kwargs)
    fig.savefig(filename + ".pdf", dpi=dpi, **kwargs)
