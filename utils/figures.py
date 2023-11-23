import os
from pathlib import PosixPath, Path
from typing import List, Tuple, Optional, Union, Dict, Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def open_figure(
    my_dpi: float = 96, size: float = 800, **kwargs: Any
) -> Tuple[Figure, Axes]:
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


def save_figure(
    fig: Figure,
    filename: Union[str, Path, PosixPath],
    size: Tuple[int, int] = (30, 30),
    dpi: float = 600,
    **kwargs: Any,
) -> None:
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


def print_progression(
    pops: List[int],
    filename: Optional[Union[str, Path, PosixPath]] = None,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    fig, ax = open_figure(**kwargs)
    ax.plot(np.arange(0, len(pops)), pops)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Total Population")
    ax.set_xlim(0, len(pops) - 1)
    ax.set_ylim(0, max(pops) * 1.1)
    ax.grid()
    fig.show()
    if filename is not None:
        save_figure(fig, filename=filename, size=(10, 10), formats=["png"])
    return fig, ax
