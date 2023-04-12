import json
from pathlib import Path, PosixPath

import numpy as np
import pandas as pd

from anno1800skyscraper.house import House
from anno1800skyscraper.map import Map


def read_map_from_csv(filename: str | Path | PosixPath):
    data = pd.read_csv(filename, delimiter=",")
    width = data.loc[:, ["loc_x"]].values.max() + 3
    height = data.loc[:, ["loc_y"]].values.max() + 3
    map = Map(width=width, height=height)
    for _, row in data.iterrows():
        x = row["loc_x"]
        y = row["loc_y"]
        level = row["level"]
        type = row["type"]
        if level == "random":
            if type == 1:
                level = np.random.randint(5) + 1
            else:
                level = np.random.randint(3) + 1
        else:
            level = int(level)
        house = House(x=x, y=y, level=level, type=type)
        map.add_house(house)
    map.create_adjacencies()
    return map


def read_map_from_anno_designer(filename: str | Path | PosixPath):
    with open(filename) as f:
        data: dict = json.load(f)
        houses = []
        for object in data.get("Objects"):
            idf = object.get("Identifier")
            if not idf.lower().__contains__("skyscraper"):
                continue
            loc_x, loc_y = [int(i) for i in object.get("Position").split(",")]
            type = 0 if int(idf.split("_SkyScraper_")[1][0]) == 4 else 1
            level = int(idf.split("_SkyScraper_")[1][-1])
            house = House(x=loc_x, y=loc_y, level=level, type=type)
            houses.append(house)
        width = max([h.x for h in houses]) + 3
        height = max([h.y for h in houses]) + 3
        map = Map(width=width, height=height)
        for house in houses:
            map.add_house(house)
        map.create_adjacencies()
        return map


def write_map_to_csv(map: Map, filename: str | Path | PosixPath):
    vals = []
    for house in map.houses.values():
        vals.append({
            "loc_x": house.x,
            "loc_y": house.y,
            "level": house.level,
            "type": house.type.value,
        })
    df = pd.DataFrame(vals)
    df.to_csv(filename, sep=",", index=False)
