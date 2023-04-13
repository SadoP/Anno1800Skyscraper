import argparse
from pathlib import Path
import sys
from anno1800skyscraper.map import Map
from utils.figures import print_progression
sys.setrecursionlimit(10000)
parser = argparse.ArgumentParser(
                    prog="Anno1800SkyscraperOptimizer",
                    description="This tool finds the (near) optimal distribution of houses for "
                                "any given skyscraper layout"
)
parser.add_argument("-d", "--dir", default="./layouts/realistic")
parser.add_argument("-e", "--epochs", default=10000, type=int)
parser.add_argument("-c", "--change", default=".05")
parser.add_argument("--mode")
parser.add_argument("--host")
parser.add_argument("--port")
args = parser.parse_args()

change = args.change
change = int(change) if change.isdigit() else float(change)
folder = Path(args.dir)
epochs = args.epochs
try:
    in_file = next(folder.glob(f"*.ad"))
except StopIteration:
    raise ValueError(f"Input File in {folder} not found")
out_file = folder / (in_file.stem + "_out.ad")

map = Map.load_from_ad(in_file)

if isinstance(change, int) and change > 0:
    n_change = max(change, 1)
elif isinstance(change, float) and 0 < change <= 1:
    n_change = max(int(len(map.houses.keys()) * change), 1)
else:
    raise ValueError("Change has to be given as positive integer or float between 0 and 1")

map.print_housemap(tight_layout=True, print_labels=True,
                   filename=folder / in_file.name.split('.')[0])

if out_file.exists():
    map = Map.load_from_ad(out_file)


map, pops = map.optimize(map, epochs, n_change)
map.save_to_ad(out_file)

map.print_housemap(tight_layout=True, print_labels=True,
                   filename=folder / out_file.name.split('.')[0])
print_progression(pops, tight_layout=True)

