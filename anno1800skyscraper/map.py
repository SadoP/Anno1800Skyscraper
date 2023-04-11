import itertools
from typing import List

import numpy as np

from anno1800skyscraper.house import House
from utils.figures import open_figure


class Map:
    def __init__(self):
        self.l = 32
        self.x_min: int = 0
        self.x_max: int = 0
        self.y_min: int = self.l
        self.y_max: int = self.l
        self.coord_map: np.ndarray = np.chararray((self.l, self.l), itemsize=8)
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
            raise ValueError("Coordinates not of unique house")
        if hashes[0] == "":
            return 0
        return self.house_by_hash(hashes[0])

    def house_by_hash(self, hash) -> House:
        return self.houses.get(hash)

    def add_house(self, house: House) -> None:
        if self.house_exists(house):
            raise ValueError("House already exists")
        if self.house_by_coords(house.x, house.y) != 0:
            raise ValueError("Placement for house occupied")
        self.coord_map[house.x:house.x + 2, house.y:house.y + 2] = house.id
        self.houses[house.id] = house

    def print_housemap(self):
        for house in self.houses.values():
            print(house)
        print(f"Total inhabitants: {self.total_inhabitants}")

        fig, ax = open_figure()
        ax.imshow(self.categorical_coords_map, cmap="tab20")
        fig.show()

    @property
    def categorical_coords_map(self):
        vals = np.unique(self.coord_map)
        new_map = np.zeros((self.l, self.l), dtype=int)
        i = 0
        for v in vals:
            new_map[self.coord_map == v] = i
            i += 1
        return new_map

    @property
    def total_inhabitants(self):
        return sum([h.inhabitants for h in self.houses.values()])

map = Map()
houses = [
    House(0, 0, 1, 1),
    House(1, 2, 1, 1),
    House(2, 0, 1, 1),
    House(3, 2, 5, 1),
    House(0, 7, 1, 1),
    House(7, 0, 1, 1)
]

for h in houses:
    map.add_house(h)


for h1, h2 in itertools.product(map.houses.values(), map.houses.values()):
    h1.adjacencyMap.add_adjacency(h2)

map.print_housemap()

