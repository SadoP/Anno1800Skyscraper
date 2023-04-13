import argparse
from pathlib import Path
import sys
from anno1800skyscraper.map import Map
from utils.figures import save_figure, print_progression
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

map: Map = Map.load_from_ad(in_file)

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
    map, pops = map.optimize(epochs, n_change)
    map.save_to_ad(out_file)
    fig, _ = map.print_housemap(tight_layout=True, print_labels=True)
    save_figure(fig, folder / out_file.name.split('.')[0],
                size=(max(map.width*2/3, 15), max(map.height*2/3, 15)), formats=["png"])

    fig, ax = print_progression(pops, tight_layout=True)
    save_figure(fig, folder / out_file.name.replace("_out.csv", "_prog"), size=(10, 10),
                formats=["png"])
else:
    map = Map.load_from_ad(out_file)
    fig, _ = map.print_housemap(tight_layout=True, print_labels=True)
    save_figure(fig, folder / out_file.name.split('.')[0],
                size=(max(map.width*2/3, 15), max(map.height*2/3, 15)), formats=["png"])
