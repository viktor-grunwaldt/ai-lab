#!/usr/bin/env python
#
import sys


def is_mergable(row, hint):
    pass


if sys.version_info[:2] < (3, 10):
    raise Exception(
        "Int.bit_count() is new in version 3.10, please use bin().count('1')"
    )


# edit distance
def calc_dist(row: str, hint: int):
    white_spaces = len(row) - hint
    if hint == 0:
        return row.count("1")

    ones = (1 << hint) - 1
    try:
        # count from the right side, as left is the MSB
        begin = row[::-1].index("1")
    except ValueError:
        return hint
    # create all possible solutions
    possible_solutions = [ones << i for i in range(begin, white_spaces + 1)]
    bin_row = int(row, 2)
    # calculate amount of common bits
    sols_dist = [(bin_row & sol).bit_count() for sol in possible_solutions]
    closest = max(sols_dist)
    # keep solutions with lowest dist
    # solutions = [sol for dist, sol in zip(sols_dist, possible_solutions) if dist != closest]
    sol_idx = sols_dist.index(closest)
    ans = (possible_solutions[sol_idx] ^ bin_row).bit_count()
    return ans


def dist_partial(a: int):
    return lambda b: (a ^ b).bit_count()


def dist_func(row: int, sol_set: set[int]) -> int:
    key_func = dist_partial(row)
    return min(map(key_func, sol_set))


def calc_dist2(row: str, hint: int):
    white_spaces = len(row) - hint
    if hint == 0:
        return row.count("1")

    ones = (1 << hint) - 1
    try:
        # count from the right side, as left is the MSB
        begin = row[::-1].index("1")
    except ValueError:
        return hint

    possible_solutions = [ones << i for i in range(begin, white_spaces + 1)]
    bin_row = int(row, 2)
    return dist_func(bin_row, possible_solutions)


def parse_line(line: str) -> tuple[str, int]:
    l, r = line.split()
    return l, int(r)


if __name__ == "__main__":
    try:
        input = list(map(parse_line, open("zad4_input.txt", "r").read().splitlines()))
        output = "\n".join(str(calc_dist2(*arg)) for arg in input)
        # output2 = "\n".join(str(calc_dist2(*arg)) for arg in input)
        open("zad4_output.txt", "w").write(output)
    except IOError:
        print("test files are missing")
