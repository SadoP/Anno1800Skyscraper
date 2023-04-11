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
