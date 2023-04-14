from enum import Enum


class HousingOptions(Enum):
    ENGINEER = 0
    INVESTOR = 1


INVESTORSKYSCRAPERCOLORS = {
    1: {
        "A": 255,
        "R": 3,
        "G": 94,
        "B": 94
    },
    2: {
        "A": 255,
        "R": 0,
        "G": 128,
        "B": 128
    },
    3: {
        "A": 255,
        "R": 68,
        "G": 166,
        "B": 166
    },
    4: {

        "A": 255,
        "R": 105,
        "G": 196,
        "B": 196
    },
    5: {
        "A": 255,
        "R": 161,
        "G": 234,
        "B": 234
    }
}

ENGINEERSKYSCRAPERCOLORS = {
    1: {
        "A": 255,
        "R": 97,
        "G": 118,
        "B": 136
    },
    2: {
        "A": 255,
        "R": 144,
        "G": 165,
        "B": 183
    },
    3: {
        "A": 255,
        "R": 169,
        "G": 195,
        "B": 237
    }
}


class InvestorSkyscraper(Enum):
    A7_residence_SkyScraper_5lvl1 = 1
    A7_residence_SkyScraper_5lvl2 = 2
    A7_residence_SkyScraper_5lvl3 = 3
    A7_residence_SkyScraper_5lvl4 = 4
    A7_residence_SkyScraper_5lvl5 = 5


class EngineerSkyscraper(Enum):
    A7_residence_SkyScraper_4lvl1 = 1
    A7_residence_SkyScraper_4lvl2 = 2
    A7_residence_SkyScraper_4lvl3 = 3
