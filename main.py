import argparse
import copy
import glob
import os
from pathlib import Path

from tqdm import trange
import numpy as np

from utils.figures import save_figure
from utils.map import read_map_from_csv, write_map_to_csv

parser = argparse.ArgumentParser(
                    prog="Anno1800SkyscraperOptimizer",
                    description="This tool finds the (near) optimal distribution of houses for "
                                "any given skyscraper layout"
)
parser.add_argument("-d", "--dir", default="./layouts/example")
parser.add_argument("-e", "--epochs", default=10000, type=int)
parser.add_argument("-c", "--change", default=.05)
parser.add_argument("-w", "--width", default=34, type=int)
args = parser.parse_args()

change = args.change
change = int(change) if change.isdigit() else float(change)
folder = Path(args.dir)
epochs = args.epochs
width = args.width
try:
    in_file = next(folder.glob("*_in.csv"))
except StopIteration:
    raise ValueError(f"Input File in {folder} not found")
out_file = folder / in_file.name.replace("_in", "_out")

map = read_map_from_csv(in_file, width=width)

if isinstance(change, int) and change > 0:
    n_change = max(change, 1)
elif isinstance(change, float) and 0 < change <= 1:
    n_change = max(int(len(map.houses.keys()) * change), 1)
else:
    raise ValueError("Change has to be given as positive integer or float between 0 and 1")


fig, _ = map.print_housemap(tight_layout=True)
save_figure(fig, folder / in_file.name.split('.')[0], size=(20, 20), formats=["png"])
epoch_range = trange(epochs, unit="epoch")
for e in epoch_range:
    map_new = copy.deepcopy(map)
    house_keys = np.random.choice(list(map_new.houses.keys()), n_change)
    tot = map_new.total_inhabitants
    for key in house_keys:
        map_new.house_by_hash(key).increment_level() if np.random.random() < .5 else \
            map_new.house_by_hash(key).decrement_level()

    if map_new.total_inhabitants >= map.total_inhabitants:
        map = map_new
    epoch_range.set_postfix({"Total": tot})

fig, _ = map.print_housemap(tight_layout=True)

write_map_to_csv(map, out_file)
save_figure(fig, folder / out_file.name.split('.')[0], size=(20, 20), formats=["png"])
