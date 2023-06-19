from more_itertools import flatten
from itertools import product
from string import ascii_uppercase


def add_sq(kw, pos, size):
    x, y = pos
    dx = size
    dy = size

    for i, j in product(range(x, x + dx), range(y, y + dy)):
        if kw[i][j] != ".":
            print(kw[i][j])
            return False

    for i, j in product(range(x, x + dx), range(y, y + dy)):
        kw[i][j] = ascii_uppercase[size - 1]

    return True


def is_corner(kw, pos):
    x, y = pos
    slice = []
    for i, j in product(range(x, x + 1), range(y, y + 1)):
        slice.append(kw[i][j])
    dots = slice.count(".")
    if dots != 1:
        return None

    corner_pos = slice.index(".")
    return (x + (corner_pos // 2), y + (corner_pos % 2))


def solve():
    kw = [["."] * 72 for _ in range(72)]
    for i in range(72):
        kw[0][i] = ""
        kw[71][i] = ""
        kw[i][0] = ""
        kw[i][71] = ""

    res = add_sq(kw, (1, 1), 24)
    if not res:
        print("fail")
        return

    for line in kw:
        print("".join(line))
    print(sum(1 for c in flatten(kw) if c == "."))


solve()
