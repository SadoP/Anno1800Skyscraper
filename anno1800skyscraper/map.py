import itertools
from typing import List

import matplotlib
import numpy as np
from matplotlib import colors, pyplot as plt

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

    def print_housemap(self) -> (plt.Figure, plt.Axes):
        for house in self.houses.values():
            print(house)
        print(f"Total inhabitants: {self.total_inhabitants}")

        bounds = [a-0.5 for a in [0, 1, 2, 3, 4, 5, 6]]
        cmap = matplotlib.colormaps["Set1"]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        fig, ax = open_figure()
        im = ax.imshow(self.categorical_coords_map, origin='lower', cmap=cmap, norm=norm,
                       extent=[0, self.width, 0, self.width])
        fig.colorbar(im, ax=ax, cmap=cmap, norm=norm, boundaries=bounds,
                     ticks=[b + 0.5 for b in bounds])
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.width)
        fig.show()
        return fig, ax

    @property
    def categorical_coords_map(self):
        vals = np.unique(self.coord_map)
        new_map = np.zeros((self.width, self.width), dtype=int)
        i = 0
        for v in vals:
            if v == "":
                continue
            new_map[self.coord_map == v] = self.house_by_hash(v.decode("utf-8")).level
            i += 1
        return new_map

    @property
    def total_inhabitants(self):
        return sum([h.inhabitants for h in self.houses.values()])

    def create_adjacencies(self):
        for h1, h2 in itertools.product(self.houses.values(), self.houses.values()):
            h1.adjacencyMap.add_adjacency(h2)
