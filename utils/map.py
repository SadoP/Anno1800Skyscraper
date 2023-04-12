from pathlib import Path, PosixPath

import numpy as np
import pandas as pd

from anno1800skyscraper.house import House
from anno1800skyscraper.map import Map


def read_map_from_csv(filename: str | Path | PosixPath, width: int = 34):
    map = Map(width=width)
    data = pd.read_csv(filename, delimiter=",")
    for _, row in data.iterrows():
        x = row["loc_x"]
        y = row["loc_y"]
        level = row["level"]
        type = row["type"]
        if level == "random":
            if type == 1:
                level = np.random.randint(5)+1
            else:
                level = np.random.randint(3)+1
        else:
            level = int(level)
        house = House(x=x, y=y, level=level, type=type)
        map.add_house(house)
    map.create_adjacencies()
    return map


def write_map_to_csv(map:Map, filename: str | Path | PosixPath):
    vals = []
    for house in map.houses.values():
        vals .append({
            "loc_x": house.x,
            "loc_y": house.y,
            "level": house.level,
            "type": house.type.value,
        })
    df = pd.DataFrame(vals)
    df.to_csv(filename, sep=",", index=False)
