from __future__ import annotations

import math
from enum import Enum
import hashlib

import numpy as np


class HousingOptions(Enum):
    ENGINEER = 0
    INVESTOR = 1


class InvestorSkyscraper(Enum):
    A7_residence_SkyScraper_5lvl1 = 1
    A7_residence_SkyScraper_5lvl2 = 2
    A7_residence_SkyScraper_5lvl3 = 3
    A7_residence_SkyScraper_5lvl4 = 4
    A7_residence_SkyScraper_5lvl5 = 5


class EngineerSkyscraper(Enum):
    A7_residence_SkyScraper_4lvl1 = 1
    A7_residence_SkyScraper_4lvl2 = 2
    A7_residence_SkyScraper_4lvl3 = 3


class AdjacencyMap:
    def __init__(self, center_house: House):
        self.center_house: House = center_house
        self.adjacents: dict[str, House] = {}

    def add_adjacency(self, house: House):
        if house == self.center_house:
            return
        if math.sqrt(
                (self.center_house.x - house.x) ** 2 + (self.center_house.y - house.y) ** 2
        ) > 7:
            return
        if self.in_adjacency(house):
            return
        self.adjacents[house.id] = house

    def in_adjacency(self, house: House):
        return house.id in self.adjacents.keys()

    @property
    def adjacents(self) -> dict[str, House]:
        return self._adjacents

    @adjacents.setter
    def adjacents(self, value):
        self._adjacents = value


class House:
    def __init__(self, x: int, y: int, level: int, type: int):
        if x < 0 or y < 0 or \
                not isinstance(x, (int, np.integer)) or \
                not isinstance(y, (int, np.integer)):
            raise ValueError(f"X and Y coordinates have to be given as positive integers but were"
                             f"{x} and {y}."
                             "The Coordinate refers to their lower left corner.")
        self.x: int = x
        self.y: int = y
        self.type: HousingOptions = HousingOptions(type)
        self.level: int = level
        self.adjacencyMap = AdjacencyMap(self)

    @property
    def id(self):
        return hashlib.sha256(str(id(self)).encode('ASCII')).hexdigest()[:8]

    @property
    def level(self):
        return self._level

    @property
    def max_level(self):
        return 3 if self.type.value == 0 else 5

    @property
    def min_level(self):
        return 1

    @level.setter
    def level(self, value):
        if value < 1 or value > self.max_level or not isinstance(value, (int, np.integer)):
            raise ValueError(f"Level has to be an integer between {self.min_level} and "
                             f"{self.max_level} but was {value}")
        self._level = value

    def increment_level(self):
        self.level = min(self.max_level, self.level + 1)

    def decrement_level(self):
        self.level = max(self.min_level, self.level - 1)

    @property
    def panorama(self):
        panorama = self.level
        for house in self.adjacents.values():
            panorama += self.compare_house_levels(self, house)
        return np.clip(panorama, 0, 5)

    @property
    def adjacents(self) -> dict[str, House]:
        return {
            house.id: house for house in self.adjacencyMap.adjacents.values() if
            self.calc_house_distance(self, house) <= self.max_dist_by_level(self.level)
        }

    @staticmethod
    def compare_house_levels(own: House, other: House) -> int:
        if own.level == other.level:
            if own.type == other.type:
                return -1
            return 1
        if own.level < other.level:
            return -1
        if own.level > other.level:
            return 1
        return 0

    @staticmethod
    def calc_house_distance(own: House, other: House) -> float:
        return math.sqrt((own.x - other.x) ** 2 + (other.y - other.y) ** 2)

    @staticmethod
    def max_dist_by_level(level: int):
        return {
            1: 4,
            2: 4.25,
            3: 5,
            4: 6,
            5: 6.75
        }.get(level)

    @property
    def inhabitants(self):
        if self.type.value == 0:
            return self.__eng_inhabitants
        return self.__inv_inhabitants

    @property
    def __eng_inhabitants(self):
        return [136, 171, 196][self.level - 1] + [0, 50, 39, 40, 39, 41][self.panorama]

    @property
    def __inv_inhabitants(self):
        return [197, 239, 283, 331, 381][self.level - 1] + [0, 80, 139, 193, 253, 319][
            self.panorama]

    @property
    def annoDesignerIdentifier(self):
        return EngineerSkyscraper(self.level) if self.type == 0 else InvestorSkyscraper(self.level)

    @property
    def annoDesignerPosition(self):
        return f"{self.x, self.y}"

    def __repr__(self):
        return f"Level {self.level} {self.type.name} residence {self.id} at location ({self.x}," \
               f" {self.y}) with {self.panorama} panorama, {self.inhabitants} inhabitants and" \
               f" {len(self.adjacents)} adjacencies"
