from dataclasses import dataclass
from itertools import groupby
import random

Grid = list[list[int]]


@dataclass
class Meta:
    row_len: int
    col_len: int
    row_clues: tuple[int]
    col_clues: tuple[int]


def read_input():
    with open("zad5_input.txt", "r") as f:
        data = f.read().splitlines()
    size, rest = data[0], data[1:]
    x, y = tuple(map(int, size.split()))
    rest = tuple(int(row) for row in rest)
    return Meta(x, y, rest[:x], rest[x:])


def check_row(row: list[int], hint: int) -> bool:
    blocks = (sum(1 for _ in it) for val, it in groupby(row) if val)
    return next(blocks) == hint and next(blocks, None) is None


def row_dist(row: list[int], hint: int) -> int:
    blanks = len(row) - hint
    solution = [1] * hint + [0] * blanks
    dist = len(row)
    for i in range(blanks):
        dist = min(dist, sum(int(a != b) for a, b in zip(row, solution)))
        solution[i] = 0
        solution[hint + i] = 1

    return dist


def is_solved(grid: Grid, meta: Meta):
    check_rows = all(map(check_row, grid, meta.row_clues))
    if not check_rows:
        return False

    return all(map(check_row, zip(*grid), meta.col_clues))


def solve(meta: Meta, prob: int):
    # impl me
    grid = [[0] * meta.row_len for _ in range(meta.col_len)]
    while not is_solved(grid, meta):
        # pick a row
        is_breaking_things = prob > random.randrange(100)
        return 

        # choose best pixel

    return grid


if __name__ == "__main__":
    meta = read_input()
    print(meta.row_clues, meta.col_clues)
    solve(meta, 3)
