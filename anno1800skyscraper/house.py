from __future__ import annotations

import hashlib
import math
from typing import Dict

import numpy as np

from anno1800skyscraper.const import (
    HousingOptions,
    EngineerSkyscraper,
    InvestorSkyscraper,
    INVESTORSKYSCRAPERCOLORS,
    ENGINEERSKYSCRAPERCOLORS,
)


class AdjacencyMap:
    def __init__(self, center_house: House):
        self.center_house: House = center_house
        self.adjacents: dict[str, House] = {}

    def add_adjacency(self, house: House) -> None:
        if house == self.center_house:
            return
        if (
            math.sqrt(
                (self.center_house.x - house.x) ** 2
                + (self.center_house.y - house.y) ** 2
            )
            > 7
        ):
            return
        if self.in_adjacency(house):
            return
        self.adjacents[house.id] = house

    def in_adjacency(self, house: House) -> bool:
        return house.id in self.adjacents.keys()

    @property
    def adjacents(self) -> dict[str, House]:
        return self._adjacents

    @adjacents.setter
    def adjacents(self, value: dict[str, House]) -> None:
        self._adjacents = value


class House:
    def __init__(self, x: int, y: int, level: int, house_type: int):
        if not isinstance(x, (int, np.integer)) or not isinstance(y, (int, np.integer)):
            raise ValueError(
                f"X and Y coordinates have to be given as integers but were"
                f"{x} and {y}."
                "The Coordinate refers to their lower left corner."
            )
        self.x: int = x
        self.y: int = y
        self.type: HousingOptions = HousingOptions(house_type)
        self.level: int = level
        self.adjacency_map = AdjacencyMap(self)

    @property
    def id(self) -> str:
        return hashlib.sha256(str(id(self)).encode("ASCII")).hexdigest()[:8]

    @property
    def max_level(self) -> int:
        return 3 if self.type.value == 0 else 5

    @property
    def min_level(self) -> int:
        return 1

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        if (
            value < 1
            or value > self.max_level
            or not isinstance(value, (int, np.integer))
        ):
            raise ValueError(
                f"Level has to be an integer between {self.min_level} and "
                f"{self.max_level} but was {value}"
            )
        self._level = value

    def increment_level(self) -> None:
        self.level = min(self.max_level, self.level + 1)

    def decrement_level(self) -> None:
        self.level = max(self.min_level, self.level - 1)

    @property
    def panorama(self) -> int:
        panorama = self.level
        for house in self.adjacents.values():
            panorama += self.compare_house_levels(self, house)
        return int(np.clip(panorama, 0, 5))

    @property
    def adjacents(self) -> dict[str, House]:
        return {
            house.id: house
            for house in self.adjacency_map.adjacents.values()
            if self.calc_house_distance(self, house) <= self.radius
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
    def max_dist_by_level(level: int) -> float:
        vals = {1: 4, 2: 4.25, 3: 5, 4: 6, 5: 6.75}
        if level not in vals.keys():
            raise ValueError
        out = vals.get(level)
        if out is None:
            raise KeyError
        return out

    @property
    def radius(self) -> float:
        return self.max_dist_by_level(self.level)

    @property
    def inhabitants(self) -> int:
        if self.type.value == 0:
            return self.__eng_inhabitants
        return self.__inv_inhabitants

    @property
    def __eng_inhabitants(self) -> int:
        return [136, 171, 196][self.level - 1] + [0, 50, 39, 40, 39, 41][self.panorama]

    @property
    def __inv_inhabitants(self) -> int:
        return [197, 239, 283, 331, 381][self.level - 1] + [0, 80, 139, 193, 253, 319][
            self.panorama
        ]

    @property
    def annoDesignerIdentifier(self) -> EngineerSkyscraper | InvestorSkyscraper:
        return (
            EngineerSkyscraper(self.level)
            if self.type.value == 0
            else InvestorSkyscraper(self.level)
        )

    @property
    def annoDesignerPosition(self) -> str:
        return f"{self.x, self.y}"

    @property
    def annoDesignerColor(self) -> Dict[str, int]:
        return (
            ENGINEERSKYSCRAPERCOLORS.get(
                self.level, {"A": 255, "R": 255, "G": 255, "B": 255}
            )
            if self.type.value == 0
            else INVESTORSKYSCRAPERCOLORS.get(
                self.level, {"A": 255, "R": 255, "G": 255, "B": 255}
            )
        )

    def __repr__(self) -> str:
        return (
            f"Level {self.level} {self.type.name} residence {self.id} at location ({self.x},"
            f" {self.y}) with {self.panorama} panorama, {self.inhabitants} inhabitants and"
            f" {len(self.adjacents)} adjacencies"
        )
