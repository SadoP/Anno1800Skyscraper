import unittest
from anno1800skyscraper.house import House
from anno1800skyscraper.map import Map


class TestHouse(unittest.TestCase):
    def test_comp(self) -> None:
        # Comparing same residences
        for residence in [0, 1]:
            for level in range(1, 5):
                if residence == 0 and level > 2:
                    continue
                house_large = House(0, 0, level + 1, residence)
                house_small = House(0, 0, level, residence)
                assert House.compare_house_levels(house_small, house_large) == -1
                assert House.compare_house_levels(house_large, house_small) == 1
                assert House.compare_house_levels(house_small, house_small) == -1
                assert House.compare_house_levels(house_large, house_large) == -1
        # Comparing different residences
        for level in range(1, 3):
            house_ENG = House(0, 0, level, 0)
            house_INV = House(0, 0, level, 1)
            assert House.compare_house_levels(house_ENG, house_INV) == 1
            assert House.compare_house_levels(house_INV, house_ENG) == 1

    def test_issue_9(self) -> None:
        """Minimal example to reproduce
        https://github.com/SadoP/Anno1800Skyscraper/issues/9
        Just focusing on the middle house like this:
        552|24
        4 3|5
        525|55
        ------
        255|35
        Focus is on the house in the middle (3), the bars denote a road,
        otherwise houses are adjacent.
        """
        # First row:
        house_00: House = House(0, 0, 5, 1)
        house_10: House = House(3, 0, 2, 1)
        house_20: House = House(6, 0, 5, 1)
        house_30: House = House(10, 0, 2, 1)
        house_40: House = House(13, 0, 4, 1)

        # Second row (two holes):
        house_01: House = House(0, 3, 4, 1)
        house_21: House = House(6, 3, 3, 1)  # <- House of interest
        house_31: House = House(10, 3, 5, 1)

        # Third row:
        house_02: House = House(0, 6, 5, 1)
        house_12: House = House(3, 6, 2, 1)
        house_22: House = House(6, 6, 5, 1)
        house_32: House = House(10, 6, 5, 1)
        house_42: House = House(13, 6, 5, 1)

        # Fourth row:
        house_03: House = House(0, 10, 2, 1)
        house_13: House = House(3, 10, 5, 1)
        house_23: House = House(6, 10, 5, 1)
        house_33: House = House(10, 10, 3, 1)
        house_43: House = House(13, 10, 5, 1)

        all_houses = [
            house_00,
            house_10,
            house_20,
            house_30,
            house_40,
            house_01,
            house_21,
            house_31,
            house_02,
            house_12,
            house_22,
            house_32,
            house_42,
            house_03,
            house_13,
            house_23,
            house_33,
            house_43,
        ]

        house_map = Map(width=15, height=15)
        for h in all_houses:
            house_map.add_house(h)
        house_map.create_adjacencies()
        house_map.print_housemap(verbose=True, print_labels=True)

        assert house_21.panorama == 2
        assert len(house_21.adjacents) == 7
