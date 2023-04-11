import copy
import itertools

from tqdm import tqdm

from anno1800skyscraper.house import House
from anno1800skyscraper.map import Map
import numpy as np

def create_2x2_grid():
    map = Map(width=33)
    houses = []
    for i, j in itertools.product(range(7), range(7)):
        houses.extend([
            House(i*5, j*5+0, np.random.randint(5)+1, 1),
            House(i*5, j*5+2, np.random.randint(5)+1, 1),
            House(i*5+2, j*5+0, np.random.randint(5)+1, 1),
            House(i*5+2, j*5+2, np.random.randint(5)+1, 1),
        ])
    for h in houses:
        map.add_house(h)
    map.create_adjacencies()
    return map

map = create_2x2_grid()
map.print_housemap()
n_change = int(len(map.houses.keys()) * 0.05)
n_diff = 1
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

