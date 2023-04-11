import unittest
from anno1800skyscraper.house import House


class TestHouse(unittest.TestCase):
    def test_comp(self):
        # Comparing same residences
        for residence in [0, 1]:
            for level in range(1, 5):
                house_large = House(0, 0, level + 1, residence)
                house_small = House(0, 0, level, residence)
                assert House.compare_house_levels(house_small, house_large) == -1
                assert House.compare_house_levels(house_large, house_small) == 1
                assert House.compare_house_levels(house_small, house_small) == 0
                assert House.compare_house_levels(house_large, house_large) == 0
        # Comparing different residences
        for level in range(1, 6):
            house_ENG = House(0, 0, level, 0)
            house_INV = House(0, 0, level, 1)
            assert House.compare_house_levels(house_ENG, house_INV) == 1
            assert House.compare_house_levels(house_INV, house_ENG) == 1

