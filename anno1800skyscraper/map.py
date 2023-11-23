from __future__ import annotations

import copy
import itertools
import json
from pathlib import Path, PosixPath
from typing import List, Dict, Any, Union, Optional, Tuple

import matplotlib
import numpy as np
from matplotlib import colors
from matplotlib.colors import LinearSegmentedColormap, Colormap
from matplotlib.patches import Rectangle
from tqdm import trange
from tqdm.std import tqdm

from anno1800skyscraper.const import InvestorSkyscraper, EngineerSkyscraper
from anno1800skyscraper.house import House
from utils.figures import open_figure, save_figure


class Map:
    def __init__(
        self, width: int = 32, height: int = 32, x_offset: int = 0, y_offset: int = 0
    ):
        self.width = width + 2
        self.height = height + 2
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.coord_map: np.chararray[Any, np.dtype[np.bytes_]] = np.chararray(
            (self.width, self.height), itemsize=8
        )
        self.coord_map[:] = ""
        self.houses: dict[str, House] = {}
        self.ad_file: Union[str, Path, PosixPath] = ""
        self.file_contents: Dict[Any, Any] = {}

    @property
    def house_hashes(self) -> List[str]:
        return list(self.houses.keys())

    def house_exists(self, house: House) -> bool:
        return house.id in self.house_hashes

    def house_by_coords(self, x: int, y: int) -> Optional[House]:
        coords = self.coord_map[x : x + 3, y : y + 3].flatten()
        hashes = np.unique(coords)
        if len(hashes) != 1:
            raise ValueError(f"Coordinates ({x}, {y}) not of unique house")
        if hashes[0] == "":
            return None
        return self.house_by_hash(hashes[0].decode("utf-8"))

    def house_by_hash(self, hash_str: str) -> House:
        house: Optional[House] = self.houses.get(hash_str)
        if not house:
            raise KeyError
        return house

    def add_house(self, house: House) -> None:
        if house.x + 3 > self.width or house.y + 3 > self.height:
            raise ValueError(
                f"House placement outside of map borders. House is at "
                f"{house.x, house.y}, map has borders {self.width, self.height}"
            )
        if self.house_exists(house):
            raise ValueError("House already exists")
        if self.house_by_coords(house.x, house.y):
            raise ValueError("Placement for house occupied")
        self.coord_map[house.x : house.x + 3, house.y : house.y + 3] = house.id
        self.houses[house.id] = house

    @staticmethod
    def optimize(house_map: Map, epochs: int, n_change: int) -> Tuple[Map, List[int]]:
        epoch_range: tqdm = trange(epochs, unit="epoch")  # type: ignore
        pops = [house_map.total_inhabitants]
        for _ in epoch_range:
            house_map_new = copy.deepcopy(house_map)
            house_keys = np.random.choice(list(house_map_new.houses.keys()), n_change)
            for key in house_keys:
                house = house_map_new.house_by_hash(key)
                if np.random.random() < 0.5:
                    house.increment_level()
                else:
                    house.decrement_level()
            if house_map_new.total_inhabitants >= house_map.total_inhabitants:
                house_map = house_map_new
            tot = house_map.total_inhabitants
            pops.append(tot)
            epoch_range.set_postfix({"Total": str(tot)})
        return house_map, pops

    def print_housemap(
        self,
        verbose: bool = False,
        print_labels: bool = False,
        filename: Optional[Union[str, Path, PosixPath]] = None,
        **kwargs: Any,
    ) -> None:
        if verbose:
            for house in self.houses.values():
                print(house)
        if not isinstance(filename, Path) and filename is not None:
            filename = Path(filename)
        print(f"Total inhabitants: {self.total_inhabitants}")
        cat_map = self.categorical_coords_map
        m = np.abs(cat_map[:, :, 0].astype(float))
        m[m == 0] = np.nan
        for i in range(2):
            if i == 0:
                bounds = np.arange(-3.5, 6.5, 1)
                matplotlib.colormaps.unregister("SpectralShrunk")
                cmap: Union[LinearSegmentedColormap, Colormap] = self.shiftedColorMap(
                    matplotlib.colormaps["RdBu"], midpoint=0.4, name="SpectralShrunk"
                )
            else:
                bounds = np.arange(-0.5, 6.5, 1)
                cmap = matplotlib.colormaps["Spectral"]
            norm = colors.BoundaryNorm(bounds, cmap.N)
            fig, ax = open_figure(**kwargs)
            im = ax.imshow(
                (cat_map[:, :, 0] * cat_map[:, :, 1]).T
                if i == 0
                else (m * cat_map[:, :, 2]).T,
                origin="lower",
                cmap=cmap,
                norm=norm,
                extent=(0, self.width, 0, self.height),
            )
            cbar = fig.colorbar(
                im,
                ax=ax,
                cmap=cmap,
                norm=norm,
                boundaries=bounds,
                ticks=bounds + 0.5,
                label="Skyscraper Level" if i == 0 else "Panorama",
            )
            if i == 0:
                ticklabels = cbar.ax.get_ymajorticklabels()
                newTicklabels = []
                for ticklabel in ticklabels:
                    tl = ticklabel
                    text = tl.get_text().replace("\u2212", "-")
                    if text[0] == "-":
                        text = text.replace("-", "Engineer Level ")
                    elif text == "0":
                        text = "empty"
                    else:
                        text = "Investor Level " + text
                    tl.set_text(text)
                    newTicklabels.append(tl)
                cbar.ax.set_yticklabels(newTicklabels)
            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)
            ax.invert_yaxis()
            ax.set_title(f"Total inhabitants: {self.total_inhabitants}")
            for house in self.houses.values():
                if print_labels:
                    ax.text(
                        x=house.x + 1.5,
                        y=house.y + 1.5,
                        s=("I" if house.type.value else "E") + str(house.level),
                        horizontalalignment="center",
                        verticalalignment="center",
                    )

                ax.add_patch(
                    Rectangle(
                        (house.x, house.y), 3, 3, edgecolor="black", fill=False, lw=1
                    )
                )
            fig.show()
            if filename is not None:
                if i == 0:
                    fname = filename.parent / (filename.stem + "_houses")
                else:
                    fname = filename.parent / (filename.stem + "_pan")
                save_figure(
                    fig,
                    filename=fname,
                    size=(
                        np.clip(self.width * 2 / 3, 15, 75),
                        np.clip(self.height * 2 / 3, 15, 75),
                    ),
                    formats=["png"],
                )

    # Based on https://stackoverflow.com/a/20528097/16509954
    @staticmethod
    def shiftedColorMap(
        cmap: Colormap,
        start: float = 0,
        midpoint: float = 0.5,
        stop: float = 1.0,
        name: str = "shiftedcmap",
    ) -> LinearSegmentedColormap:
        """
        Function to offset the "center" of a colormap. Useful for
        data with a negative min and positive max and you want the
        middle of the colormap's dynamic range to be at zero.

        Input
        -----
          cmap : The matplotlib colormap to be altered
          start : Offset from lowest point in the colormap's range.
              Defaults to 0.0 (no lower offset). Should be between
              0.0 and `midpoint`.
          midpoint : The new center of the colormap. Defaults to
              0.5 (no shift). Should be between 0.0 and 1.0. In
              general, this should be  1 - vmax / (vmax + abs(vmin))
              For example if your data range from -15.0 to +5.0 and
              you want the center of the colormap at 0.0, `midpoint`
              should be set to  1 - 5/(5 + 15)) or 0.75
          stop : Offset from highest point in the colormap's range.
              Defaults to 1.0 (no upper offset). Should be between
              `midpoint` and 1.0.
        """
        cdict = {"red": [], "green": [], "blue": [], "alpha": []}  # type: ignore

        # regular index to compute the colors
        reg_index = np.linspace(start, stop, 257)

        # shifted index to match the data
        shift_index = np.hstack(
            [
                np.linspace(0.0, midpoint, 128, endpoint=False),
                np.linspace(midpoint, 1.0, 129, endpoint=True),
            ]
        )

        for ri, si in zip(reg_index, shift_index):
            r, g, b, a = cmap(ri)

            cdict["red"].append((si, r, r))
            cdict["green"].append((si, g, g))
            cdict["blue"].append((si, b, b))
            cdict["alpha"].append((si, a, a))

        newcmap = matplotlib.colors.LinearSegmentedColormap(name, cdict)  # type: ignore
        matplotlib.colormaps.register(cmap=newcmap)
        return newcmap

    @property
    def categorical_coords_map(self) -> np.ndarray[Any, np.dtype[Any]]:
        vals = np.unique(self.coord_map)
        new_map = np.zeros((self.width, self.height, 3), dtype=int)
        i = 0
        for v in vals:
            if v == "":
                continue
            new_map[self.coord_map == v, :] = [
                1 if self.house_by_hash(v.decode("utf-8")).type.value else -1,
                self.house_by_hash(v.decode("utf-8")).level,
                self.house_by_hash(v.decode("utf-8")).panorama,
            ]
            i += 1
        return new_map

    @property
    def total_inhabitants(self) -> int:
        return sum([h.inhabitants for h in self.houses.values()])

    def create_adjacencies(self) -> None:
        for h1, h2 in itertools.product(self.houses.values(), self.houses.values()):
            h1.adjacency_map.add_adjacency(h2)

    @staticmethod
    def load_from_ad(filename: Union[str, Path, PosixPath]) -> Map:
        with open(filename, "r") as f:
            data: Dict[Any, Any] = json.load(f)
            houses = []
            for obj in data.get("Objects"):  # type: ignore
                idf = obj.get("Identifier")
                if not idf in [e.name for e in InvestorSkyscraper] + [
                    e.name for e in EngineerSkyscraper
                ]:
                    continue
                loc_x, loc_y = [int(i) for i in obj.get("Position").split(",")]
                type = 0 if int(idf.split("_SkyScraper_")[1][0]) == 4 else 1
                level = int(idf.split("_SkyScraper_")[1][-1])
                house = House(x=loc_x, y=loc_y, level=level, house_type=type)
                houses.append(house)
            x_offset = -min([h.x for h in houses])
            y_offset = -min([h.y for h in houses])
            width = max([h.x for h in houses]) + 3
            height = max([h.y for h in houses]) + 3
            map = Map(
                width=width + x_offset,
                height=height + y_offset,
                x_offset=x_offset,
                y_offset=y_offset,
            )
            for house in houses:
                house.x = house.x + x_offset
                house.y = house.y + y_offset
                map.add_house(house)
            map.create_adjacencies()
            map.ad_file = filename
            map.file_contents = data
            return map

    def save_to_ad(self, filename: Union[str, Path, PosixPath]) -> None:
        for obj in self.file_contents.get("Objects"):  # type: ignore
            idf = obj.get("Identifier")
            if not idf in [e.name for e in InvestorSkyscraper] + [
                e.name for e in EngineerSkyscraper
            ]:
                continue
            loc_x, loc_y = [int(i) for i in obj.get("Position").split(",")]
            house = self.house_by_coords(loc_x + self.x_offset, loc_y + self.y_offset)
            if not house:
                raise ValueError("House not found")
            obj["Identifier"] = house.annoDesignerIdentifier.name
            obj["Color"] = house.annoDesignerColor
            obj["Radius"] = house.radius
        with open(filename, "w") as file:
            json.dump(self.file_contents, file)
