from random import choice, randrange
import sys
from more_itertools import flatten
from dataclasses import dataclass
import typing


# thank god it's simplified nonograms which only have one block of blacks
@dataclass
class Board:
    row_size: int
    col_size: int
    clues_col: tuple[tuple[int]]
    clues_row: tuple[tuple[int]]
    sols_row: list[set]
    sols_col: list[set]

    def __post_init__(self):
        self.possible_solutions()

    def possible_solutions(self):
        """Generates all possible solutions for each row and column of nonogram"""
        # rows
        possible_solutions_rows = [set()] * self.row_size
        for row_num, row in enumerate(self.clues_row):
            white_fields = self.row_size - sum(row)
            sols = set()
            for possible_hint in sum_permutations(len(row) + 1, white_fields):
                if 0 in possible_hint[1:-1]:
                    continue
                blocks_iterator = enumerate(imerge(possible_hint, row + (0,)))
                solution_tuple = tuple(
                    flatten((i % 2,) * width for i, width in blocks_iterator)
                )
                sols.add(bitset_to_int(solution_tuple))

            possible_solutions_rows[row_num] = sols

        # columns
        possible_solutions_cols = [set()] * self.col_size
        for col_num, col in enumerate(self.clues_col):
            white_fields = self.row_size - sum(col)
            sols = set()
            for possible_hint in sum_permutations(len(col) + 1, white_fields):
                if 0 in possible_hint[1:-1]:
                    continue
                blocks_iterator = enumerate(imerge(possible_hint, col + (0,)))
                solution_tuple = tuple(
                    flatten((i % 2,) * width for i, width in blocks_iterator)
                )
                sols.add(bitset_to_int(solution_tuple))

            possible_solutions_cols[col_num] = sols
        self.sols_row = possible_solutions_rows
        self.sols_col = possible_solutions_cols


def read_input() -> Board | None:
    with open("zad_input.txt", "r") as f:
        data = f.read().splitlines()
    size, rest = data[0], data[1:]
    size = tuple(map(int, size.split()))
    rest = tuple(tuple(map(int, row.split())) for row in rest)

    return Board(size[0], size[1], rest[size[0]:], rest[:size[0]], [set()], [set()])


def bitlist_to_str(bits: list[int], b: Board) -> str:
    return "\n".join(
        map(
            lambda x: (bin(x)[2:])
            .replace("1", "#")
            .replace("0", ".")
            .rjust(b.col_size, "."),
            bits,
        )
    )


# https://stackoverflow.com/questions/7748442/generate-all-possible-lists-of-length-n-that-sum-to-s-in-python
def sum_permutations(length, total_sum):
    if length == 1:
        yield (total_sum,)
    else:
        for value in range(total_sum + 1):
            for permutation in sum_permutations(length - 1, total_sum - value):
                yield (value,) + permutation


def imerge(a, b):
    for i, j in zip(a, b):
        yield i
        yield j


def bitset_to_int(bitlist: typing.Iterable[int]):
    return int("".join(map(str, bitlist)), base=2)


# rotates bits around by generating binary number
# basically row 0 contains oldest bits, etc..
def transpose(bits: list[int], b: Board) -> list[int]:
    # do not touch bits or they will kill you

    # bits_T = [0] * b.col_size
    # for row in bits:
    #     for i in range(b.col_size):
    #         bits_T[i] <<= 1
    #         bits_T[i] += (row & (1 << i)) >> i
    # now the columns have to be reversed
    # TODO: EXPLAIN WHY (could be bugfest) (IT WAS BUGFEST)

    strings = bitlist_to_str(bits, b).splitlines()
    strings = list(zip(*strings))
    bits_T = [
        int("".join(col).replace("#", "1").replace(".", "0"), 2) for col in strings
    ]
    return bits_T


def dist_func(row: int, sol_set: set[int]) -> int:
    key_func = lambda b: (row ^ b).bit_count()
    return min(map(key_func, sol_set))


def flip_ith_FROM_RIGHT(bits: int, i: int):
    return bits ^ (1 << i)


def flip_ith_FROM_LEFT(bits: int, i: int, width: int):
    return bits ^ (1 << (width - 1 - i))


def row_to_str(row: int, size):
    return bin(row)[2:].replace("0", ".").replace("1", "#").rjust(size, ".")


def set_pixel(bits, pixel, b: Board):
    x, y = pixel
    bits[x] = flip_ith_FROM_LEFT(bits[x], y, b.col_size)
    return bits


def find_best_pixel(row_num: int, bits: list[int], b: Board):
    row: int = bits[row_num]
    bits_T = transpose(bits, b)
    # print("column view")
    # for col in bits_T:
    #     print(row_to_str(flip_ith_FROM_RIGHT(col, row_num), b.size_row))
    # in order to go towards solving, we have to check if we have improved our score
    # so score = new - old
    # and the lowest one wins
    old_dist = dist_func(row, b.sols_row[row_num])
    # dist for row
    distances = [
        dist_func(flip_ith_FROM_LEFT(row, i, b.row_size), b.sols_row[row_num]) - old_dist
        for i in range(b.col_size)
    ]
    # print(bitlist_to_str(bits, b))
    # print("hints row:", *b.clues_row, sep="\n")
    # # dist for column
    # print(bitlist_to_str(bits_T, b))
    # print("hints col:", *b.clues_col, sep="\n")
    # print(distances)
    # distances_col = [0] * b.col_size
    # distances_col = [0 for _ in range(b.col_size)]
    for i, col in enumerate(bits_T):
        # print(f"pixel = {(row_num, i)}")
        distances[i] += dist_func(flip_ith_FROM_RIGHT(col, i), b.sols_col[i])
        distances[i] -= dist_func(col, b.sols_col[i])
    # print(distances, b.sols_col[i])
    fmin = min(distances)
    min_idx = distances.index(fmin)
    # print(f"pixel = {(row_num, min_idx)}")
    return min_idx


def is_solved(bits: list[int], b: Board):
    solved_row = all(row in row_sols for row, row_sols in zip(bits, b.sols_row))
    solved_col = all(
        col in col_sols
        for col, col_sols in zip(transpose(bits, b), b.sols_col)
    )
    return solved_col and solved_row


FAIL_CHANCE = 5  # percent


def WALKsat(
    bits: list[int],
    b: Board,
    repeats=0,
):
    if is_solved(bits, b):
        return bits

    if repeats >= (b.col_size * b.row_size) * 10:
        return "FAILED TO SOLVE AFTER {} ATTEMPTS".format(repeats)

    # break stuff
    is_break_row = randrange(100) < FAIL_CHANCE

    available_rows = [
        i for i, row in enumerate(bits) if dist_func(row, b.sols_row[i]) != 0
    ]

    # if algo is too slow, implement smart row picking
    random_rownum = (
        randrange(b.row_size)
        if is_break_row or not available_rows
        else choice(available_rows)
    )

    # if we are planning to screw with a solved column,
    # it doesn't matter if pixel is best or not
    # But if we pick an unsolved column, we roll again to check if we have to
    # pick an optimal pixel or not
    is_break_pixel = (not is_break_row) and randrange(100) < FAIL_CHANCE
    modified_pixel_index = (
        randrange(b.col_size)
        if is_break_pixel
        else find_best_pixel(random_rownum, bits, b)
    )

    bits = set_pixel(bits, (random_rownum, modified_pixel_index), b)
    # os.system("clear")
    # print(bitlist_to_str(bits, b))
    # sleep(0.025)
    return WALKsat(bits, b, repeats + 1)


def solve():
    b = read_input()
    if b is None:
        raise Exception("errors while reading input")

    # # SECOND SOLVE
    bits = [0] * b.row_size
    # bits = set_pixel(bits, (0, 0), b)
    # bits = set_pixel(bits, (4, 0), b)
    # bits = set_pixel(bits, (0, 4), b)
    # print(bitlist_to_str(bits, b))
    # print(bitlist_to_str(transpose(bits, b), b))
    # print(*b.clues_row, sep='\n')
    # print(*b.clues_col, sep='\n')
    # print(bitlist_to_str(bits, b))
    # test = [
    #     0b11111,
    #     0b11010,
    #     0b10101,
    #     0b11000,
    # ]
    # b1 = Board(4, 5, [], [], None, None)
    # print(show_bits(test, b1))
    # print(show_bits(bits, b))
    sys.setrecursionlimit(5000)
    for _ in range(10):
        res = WALKsat(bits, b)
        match res:
            case list(res):
                with open("zad_output.txt", 'w') as f:
                    f.write(bitlist_to_str(res, b))
                break
            case str(res):
                print(res)
            case anyhow:
                raise Exception(str(anyhow))


if __name__ == "__main__":
    # for col in transpose(test, 5):
    #     print(bin(col))
    # print(
    #     bin(255), bin(flip_ith_FROM_LEFT(255, 2, 8)), bin(flip_ith_FROM_RIGHT(255, 2))
    # )
    solve()
