import copy
import pandas as pd
from tqdm import trange

from anno1800skyscraper.house import House
from anno1800skyscraper.map import Map
import numpy as np

from utils.figures import save_figure


def read_map_from_csv(filename: str):
    map = Map(width=34)
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
        house = House(x=x, y=y, level=level, type=type)
        map.add_house(house)
    map.create_adjacencies()
    return map


def write_map_to_csv(map:Map, filename: str):
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

input_files = ["2x2_in.csv", "3x3_in.csv"]
output_files = ["2x2_out.csv", "3x3_out.csv"]
for input_file, output_file in zip(input_files, output_files):

    map = read_map_from_csv(input_file)
    fig, _ = map.print_housemap(tight_layout=True)
    save_figure(fig, f"./figs/{input_file.split('.')[0]}", size=(20, 20), formats=["png"])
    n_change = int(len(map.houses.keys()) * 0.05)
    epochs = trange(10000, unit="epoch")
    for e in epochs:
        map_new = copy.deepcopy(map)
        house_keys = np.random.choice(list(map_new.houses.keys()), n_change)
        tot = map_new.total_inhabitants
        for key in house_keys:
            map_new.house_by_hash(key).increment_level() if np.random.random() < .5 else \
                map_new.house_by_hash(key).decrement_level()

        if map_new.total_inhabitants >= map.total_inhabitants:
            map = map_new
        epochs.set_postfix({"Total": tot})

    fig, _ = map.print_housemap(tight_layout=True)

    write_map_to_csv(map, output_file)
    save_figure(fig, f"./figs/{output_file.split('.')[0]}", size=(20, 20), formats=["png"])
