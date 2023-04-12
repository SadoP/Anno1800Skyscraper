import itertools
from typing import List

import matplotlib
import numpy as np
from matplotlib import colors, pyplot as plt
from matplotlib.patches import Rectangle

from anno1800skyscraper.house import House
from utils.figures import open_figure


class Map:
    def __init__(self, width: int = 32):
        self.width = width
        self.x_min: int = 0
        self.x_max: int = 0
        self.y_min: int = self.width
        self.y_max: int = self.width
        self.coord_map: np.ndarray = np.chararray((self.width, self.width), itemsize=8)
        self.coord_map[:] = ""
        self.houses: dict[str, House] = {}

    @property
    def house_hashes(self) -> List[str]:
        return list(self.houses.keys())

    def house_exists(self, house) -> bool:
        return house.id in self.house_hashes

    def house_by_coords(self, x, y):
        coords = self.coord_map[x:x + 2, y:y + 2].flatten()
        hashes = np.unique(coords)
        if len(hashes) != 1:
            raise ValueError(f"Coordinates ({x}, {y}) not of unique house")
        if hashes[0] == "":
            return 0
        return self.house_by_hash(hashes[0])

    def house_by_hash(self, hash) -> House:
        return self.houses.get(hash)

    def add_house(self, house: House) -> None:
        if house.x + 2 > self.width or house.y + 2 > self.width:
            raise ValueError("House placement outside of map borders")
        if self.house_exists(house):
            raise ValueError("House already exists")
        if self.house_by_coords(house.x, house.y) != 0:
            raise ValueError("Placement for house occupied")
        self.coord_map[house.x:house.x + 2, house.y:house.y + 2] = house.id
        self.houses[house.id] = house

    def print_housemap(self, verbose=False, print_labels=False, **kwargs) -> (plt.Figure, plt.Axes):
        if verbose:
            for house in self.houses.values():
                print(house)
        print(f"Total inhabitants: {self.total_inhabitants}")

        bounds = [a-0.5 for a in [-3, -2, -1, 0, 1, 2, 3, 4, 5, 6]]
        matplotlib.colormaps.unregister("SpectralShrunk")
        cmap = self.shiftedColorMap(matplotlib.colormaps["RdBu"], midpoint=0.4,
                                    name='SpectralShrunk')
        norm = colors.BoundaryNorm(bounds, cmap.N)

        fig, ax = open_figure(**kwargs)
        cat_map = self.categorical_coords_map
        im = ax.imshow((cat_map[:, :, 0] * cat_map[:, :, 1]).T, origin='lower', cmap=cmap,
                       norm=norm, extent=[0, self.width, 0, self.width])
        cbar = fig.colorbar(im, ax=ax, cmap=cmap, norm=norm, boundaries=bounds,
                            ticks=[b + 0.5 for b in bounds], label="Skyscraper Level")
        ticklabels = cbar.ax.get_ymajorticklabels()
        newTicklabels = []
        for ticklabel in ticklabels:
            tl = ticklabel
            text = tl._text.replace(u"\u2212", "-")
            if text[0] == "-":
                text = text.replace("-", "Engineer Level ")
            elif text == "0":
                text = "empty"
            else:
                text = "Investor Level " + text
            tl._text = text
            newTicklabels.append(tl)
        cbar.ax.set_yticklabels(newTicklabels)
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.width)
        ax.set_title(f"Total inhabitants: {self.total_inhabitants}")
        for house in self.houses.values():
            if print_labels:
                ax.text(
                    x=house.x+1,
                    y=house.y+1,
                    s=("I" if house.type.value else "E") + str(house.level),
                    horizontalalignment="center",
                    verticalalignment="center"
                )
            ax.add_patch(
                Rectangle((house.x, house.y), 2, 2, edgecolor="black", fill=False, lw=1)
            )
        fig.show()
        return fig, ax

    # Based on https://stackoverflow.com/a/20528097/16509954
    @staticmethod
    def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
        """
        Function to offset the "center" of a colormap. Useful for
        data with a negative min and positive max and you want the
        middle of the colormap's dynamic range to be at zero.

        Input
        -----
          cmap : The matplotlib colormap to be altered
          start : Offset from lowest point in the colormap's range.
              Defaults to 0.0 (no lower offset). Should be between
              0.0 and `midpoint`.
          midpoint : The new center of the colormap. Defaults to
              0.5 (no shift). Should be between 0.0 and 1.0. In
              general, this should be  1 - vmax / (vmax + abs(vmin))
              For example if your data range from -15.0 to +5.0 and
              you want the center of the colormap at 0.0, `midpoint`
              should be set to  1 - 5/(5 + 15)) or 0.75
          stop : Offset from highest point in the colormap's range.
              Defaults to 1.0 (no upper offset). Should be between
              `midpoint` and 1.0.
        """
        cdict = {
            'red': [],
            'green': [],
            'blue': [],
            'alpha': []
        }

        # regular index to compute the colors
        reg_index = np.linspace(start, stop, 257)

        # shifted index to match the data
        shift_index = np.hstack([
            np.linspace(0.0, midpoint, 128, endpoint=False),
            np.linspace(midpoint, 1.0, 129, endpoint=True)
        ])

        for ri, si in zip(reg_index, shift_index):
            r, g, b, a = cmap(ri)

            cdict['red'].append((si, r, r))
            cdict['green'].append((si, g, g))
            cdict['blue'].append((si, b, b))
            cdict['alpha'].append((si, a, a))

        newcmap = matplotlib.colors.LinearSegmentedColormap(name, cdict)
        plt.register_cmap(cmap=newcmap)

        return newcmap

    @property
    def categorical_coords_map(self):
        vals = np.unique(self.coord_map)
        new_map = np.zeros((self.width, self.width, 2), dtype=int)
        i = 0
        for v in vals:
            if v == "":
                continue
            new_map[self.coord_map == v, :] = [
                1 if self.house_by_hash(v.decode("utf-8")).type.value else -1,
                self.house_by_hash(v.decode("utf-8")).level
            ]
            i += 1
        return new_map

    @property
    def total_inhabitants(self):
        return sum([h.inhabitants for h in self.houses.values()])

    def create_adjacencies(self):
        for h1, h2 in itertools.product(self.houses.values(), self.houses.values()):
            h1.adjacencyMap.add_adjacency(h2)
