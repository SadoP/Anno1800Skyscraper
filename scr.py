import itertools

for j, k in itertools.product(range(5), range(5)):
    print(f"{j * 7}, {k * 7}, random, 0")
    print(f"{j * 7}, {k * 7 + 2}, random, 0")
    print(f"{j * 7}, {k * 7 + 4}, random, 1")
    print(f"{j * 7 + 2}, {k * 7}, random, 0")
    print(f"{j * 7 + 2}, {k * 7 + 4}, random, 1")
    print(f"{j * 7 + 4}, {k * 7}, random, 0")
    print(f"{j * 7 + 4}, {k * 7 + 2}, random, 0")
    print(f"{j * 7 + 4}, {k * 7 + 4}, random, 1")
