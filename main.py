import argparse
import copy
import json
from pathlib import Path
import sys

from tqdm import trange
import numpy as np

from anno1800skyscraper.house import House
from utils.figures import save_figure, print_progression
from utils.map import read_map_from_csv, write_map_to_csv, read_map_from_anno_designer

sys.setrecursionlimit(10000)
parser = argparse.ArgumentParser(
                    prog="Anno1800SkyscraperOptimizer",
                    description="This tool finds the (near) optimal distribution of houses for "
                                "any given skyscraper layout"
)
parser.add_argument("-d", "--dir", default="./layouts/example")
parser.add_argument("-e", "--epochs", default=10000, type=int)
parser.add_argument("-c", "--change", default=".05")
parser.add_argument("-f", "--filetype", default=".ad", type=str)
parser.add_argument("--mode")
parser.add_argument("--host")
parser.add_argument("--port")
args = parser.parse_args()

filetype = args.filetype
if filetype not in [".ad", ".csv"]:
    raise ValueError("Filetype has to be .ad or .csv")
change = args.change
change = int(change) if change.isdigit() else float(change)
folder = Path(args.dir)
folder = Path("./layouts/designer")
epochs = args.epochs
try:
    in_file = next(folder.glob(f"*{filetype}"))
except StopIteration:
    raise ValueError(f"Input File in {folder} not found")
if in_file.name.__contains__("_in"):
    out_file = folder / in_file.name.replace("_in", "_out")
else:
    out_file = folder / (in_file.stem + "_out.csv")

if filetype == ".csv":
    map = read_map_from_csv(in_file)
else:
    map = read_map_from_anno_designer(in_file)

if isinstance(change, int) and change > 0:
    n_change = max(change, 1)
elif isinstance(change, float) and 0 < change <= 1:
    n_change = max(int(len(map.houses.keys()) * change), 1)
else:
    raise ValueError("Change has to be given as positive integer or float between 0 and 1")


fig, _ = map.print_housemap(tight_layout=True, print_labels=True)
save_figure(fig, folder / in_file.name.split('.')[0],
            size=(max(map.width*2/3, 15), max(map.width*2/3, 15)),
            formats=["png"])
if not out_file.exists():
    epoch_range = trange(epochs, unit="epoch")
    pops = [map.total_inhabitants]
    for e in epoch_range:
        map_new = copy.deepcopy(map)
        house_keys = np.random.choice(list(map_new.houses.keys()), n_change)
        for key in house_keys:
            map_new.house_by_hash(key).increment_level() if np.random.random() < .5 else \
                map_new.house_by_hash(key).decrement_level()

        if map_new.total_inhabitants >= map.total_inhabitants:
            map = map_new
        tot = map.total_inhabitants
        pops.append(tot)
        epoch_range.set_postfix({"Total": str(tot)})

    write_map_to_csv(map, out_file)
    fig, _ = map.print_housemap(tight_layout=True, print_labels=True)
    save_figure(fig, folder / out_file.name.split('.')[0],
                size=(max(map.width*2/3, 15), max(map.height*2/3, 15)), formats=["png"])

    fig, ax = print_progression(pops, tight_layout=True)
    save_figure(fig, folder / out_file.name.replace("_out.csv", "_prog"), size=(10, 10),
                formats=["png"])
else:
    map = read_map_from_csv(out_file)
    fig, _ = map.print_housemap(tight_layout=True, print_labels=True)
    save_figure(fig, folder / out_file.name.split('.')[0],
                size=(max(map.width*2/3, 15), max(map.height*2/3, 15)), formats=["png"])
