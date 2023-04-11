import copy
import pandas as pd
from tqdm import tqdm

from anno1800skyscraper.house import House
from anno1800skyscraper.map import Map
import numpy as np

from utils.figures import save_figure


def read_map_from_csv(filename: str):
    map = Map(width=34)
    data = pd.read_csv(filename, delimiter=",", dtype=int)
    for _, row in data.iterrows():
        x = row["loc_x"]
        y = row["loc_y"]
        level = row["level"]
        if level == "random":
            level = np.random.randint(5)+1
        type = row["type"]
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


input_file = "2x2.csv"
output_file = "2x2_out.csv"

map = read_map_from_csv(input_file)
fig, _ = map.print_housemap()
save_figure(fig, "./figs/2x2_in", size=(20, 20), formats=["png"])
n_change = int(len(map.houses.keys()) * 0.05)
epochs = 10000

print(map.total_inhabitants)
inh = []
for e in tqdm(range(epochs), unit="epoch"):
    map_new = copy.deepcopy(map)
    house_keys = np.random.choice(list(map_new.houses.keys()), n_change)
    for key in house_keys:
        map_new.house_by_hash(key).increment_level() if np.random.random() < .5 else \
            map_new.house_by_hash(key).decrement_level()

    if map_new.total_inhabitants >= map.total_inhabitants:
        print(f"New total: {map_new.total_inhabitants}")
        map = map_new
    inh.append(map.total_inhabitants)

map.print_housemap()

write_map_to_csv(map, output_file)
save_figure(fig, "./figs/2x2_out", size=(20, 20), formats=["png"])
