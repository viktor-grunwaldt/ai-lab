# import cProfile
from copy import deepcopy
from dataclasses import dataclass
from functools import reduce
# import pstats
from more_itertools import flatten
import operator
import typing

Point = tuple[int, int]


@dataclass
class Board_Metadata:
    row_size: int
    col_size: int
    clues_col: tuple[tuple[int]]
    clues_row: tuple[tuple[int]]
    rows_domain: list[set[int]]
    cols_domain: list[set[int]]

    def __post_init__(self):
        self.possible_solutions()

    def possible_solutions(self):
        """Generates all possible solutions for each row and column of nonogram"""
        # rows
        possible_solutions_rows: list[set[int]] = [set()] * self.row_size
        for row_num, row in enumerate(self.clues_row):
            white_fields = self.col_size - sum(row)
            sols: set[int] = set()
            if white_fields < 0:
                print(f"{row_num=}")
                print(f"{row=}")
                raise ValueError("more black fields than possible fields")
            for possible_hint in sum_permutations(len(row) + 1, white_fields):
                if 0 in possible_hint[1:-1]:
                    continue
                # flipping hint order here
                blocks_iterator = enumerate(imerge(possible_hint, row[::-1] + (0,)))
                solution_tuple = tuple(
                    flatten((i % 2,) * width for i, width in blocks_iterator)
                )
                sols.add(bitlist_to_int(solution_tuple))

            possible_solutions_rows[row_num] = sols

        # columns
        # WARNING: columns are flipped
        possible_solutions_cols = [set()] * self.col_size
        for col_num, col in enumerate(self.clues_col):
            white_fields = self.row_size - sum(col)
            if white_fields < 0:
                print(f"{col=}")
                print(f"{col_num=}")
                raise ValueError("more black fields than possible fields")
            sols = set()
            for possible_hint in sum_permutations(len(col) + 1, white_fields):
                if 0 in possible_hint[1:-1]:
                    continue
                # flipping hint order here
                blocks_iterator = enumerate(imerge(possible_hint, col[::-1] + (0,)))
                solution_tuple = tuple(
                    flatten((i % 2,) * width for i, width in blocks_iterator)
                )
                sols.add(bitlist_to_int(solution_tuple))

            possible_solutions_cols[col_num] = sols

        if 0 in possible_solutions_cols or 0 in possible_solutions_rows:
            raise Exception("unwinnable game")
        self.rows_domain = possible_solutions_rows
        self.cols_domain = possible_solutions_cols

    def reduce_solutions(self, rows, cols, is_black=True) -> str:
        if is_black:
            is_valid_sol = lambda a, b: a | b == a
        else:
            is_valid_sol = lambda a, b: a & b == a

        new_sols_row = []
        for row, possible_sols in zip(rows, self.rows_domain):
            sols = set(hint for hint in possible_sols if is_valid_sol(hint, row))
            if len(sols) == 0:
                return "dead end"
            new_sols_row.append(sols)

        self.rows_domain = new_sols_row
        new_sols_col = []
        for col, possible_sols in zip(cols, self.cols_domain):
            sols = set(hint for hint in possible_sols if is_valid_sol(hint, col))
            if len(sols) == 0:
                return "dead end"
            new_sols_col.append(sols)
        self.cols_domain = new_sols_col

        return "successful reduce"


class Grid:
    rows: list[int]
    cols: list[int]
    # white_ are masks which keep info where black squares are possible
    metadata: Board_Metadata

    def __init__(self, b: Board_Metadata, inverted=False) -> None:
        self.metadata = b
        if not inverted:
            self.rows = [0] * b.row_size
            self.cols = [0] * b.col_size

        else:
            self.rows = [(1 << b.col_size) - 1] * b.row_size
            self.cols = [(1 << b.row_size) - 1] * b.col_size

    def check_bounds(self, key: tuple[int, int]):
        match key:
            case (int(x), int(y)) if (
                x in range(self.metadata.row_size)
                and y in range(self.metadata.col_size)
            ):
                pass
            case (int(x), int(y)):
                raise IndexError(str(key) + " out of range")
            case _:
                raise KeyError

    def __setitem__(self, key: tuple[int, int], newvalue: bool):
        # comment me out if we need more speed
        # self.check_bounds(key)
        y, x = key

        # zero out bit
        mask = ((1 << (self.metadata.col_size + 1)) - 1) ^ (1 << x)
        self.rows[y] &= mask
        # set bit to value
        self.rows[y] |= int(newvalue) << (x)

        # zero out bit
        mask = ((1 << (self.metadata.row_size + 1)) - 1) ^ (1 << y)
        self.cols[x] &= mask
        # set bit to value
        self.cols[x] |= int(newvalue) << (y)

    def __getitem__(self, key: tuple[int, int]) -> bool:
        # comment me out if we need more speed
        # self.check_bounds(key)

        y, x = key
        row_val = self.rows[y] & (1 << x)
        # testing, comment me out for more speed
        # col_val = self.cols[x] & (1 << y)
        # assert bool(row_val) == bool(col_val)
        return bool(row_val)

    def sols_to_rows(self):
        if not self.is_solved():
            print("this will break your board")
            print("this will break your board")
            print("this will break your board")
            print("this will break your board")

        for i, sols in enumerate(self.metadata.rows_domain):
            only_sol = list(sols)[0]
            for j in range(self.metadata.col_size):
                if only_sol & 1:
                    self[i, j] = True
                only_sol >>= 1

    def to_str(self, transpose=False) -> str:
        width = self.metadata.col_size if not transpose else self.metadata.row_size
        bitslist = self.rows if not transpose else self.cols
        return "\n".join(
            map(
                lambda x: (bin(x)[2:])
                .replace("1", "#")
                .replace("0", ".")
                .rjust(width, ".")[::-1],
                bitslist,
            )
        )

    def is_solved(self) -> bool:
        solved_rows = all(len(sols) == 1 for sols in self.metadata.rows_domain)
        solved_cols = all(len(sols) == 1 for sols in self.metadata.cols_domain)
        return solved_rows and solved_cols

    def __str__(self) -> str:
        return self.to_str()

    def serialize(self) -> tuple[int]:
        return tuple(self.rows)

    def deserialize(self, rows: tuple[int], base_metadata: Board_Metadata, is_black):
        for i, row in enumerate(rows):
            for j in range(base_metadata.col_size):
                self[i, j] = bool(row & 1)
                row >>= 1

        self.metadata = base_metadata
        res = self.metadata.reduce_solutions(self.rows, self.cols, is_black)
        if res != "successful reduce":
            raise ValueError("loaded an unsolvable state")


def read_input(filename="zad_input.txt") -> Board_Metadata | None:
    with open(filename, "r") as f:
        data = f.read().splitlines()
    size, rest = data[0], data[1:]
    size = tuple(map(int, size.split()))
    rest = tuple(tuple(map(int, row.split())) for row in rest)

    return Board_Metadata(
        size[0], size[1], rest[size[0] :], rest[: size[0]], [set()], [set()]
    )


# https://stackoverflow.com/questions/7748442/generate-all-possible-lists-of-length-n-that-sum-to-s-in-python
def sum_permutations(length: int, total_sum: int) -> typing.Generator:
    if length == 1:
        yield (total_sum,)
    else:
        for value in range(total_sum + 1):
            for permutation in sum_permutations(length - 1, total_sum - value):
                yield (value,) + permutation


def imerge(a: typing.Iterable, b: typing.Iterable) -> typing.Generator:
    for i, j in zip(a, b):
        yield i
        yield j


def bitlist_to_int(bitlist: typing.Iterable[int]) -> int:
    return int("".join(map(str, bitlist)), base=2)


def wave_function_collapse_axis(
    axis_sols: list[set[int]],
    axis_rows: list[int],
    other_axis_size: int,
    bitwise_op: typing.Callable[[int, int], int],
    is_matching: typing.Callable[[int], bool],
):
    collapsed_bits = []
    for i, sols_row in enumerate(axis_sols):
        # this is the most impoprtant line of code, it will speed things up massively
        # when board is close to solve, but doesn't work if something else modifies Domain
        # if len(sols_col) == 1:
        #     continue
        # find squares which are always black
        bits_on_all = reduce(bitwise_op, sols_row)
        new_bits = bits_on_all ^ axis_rows[i]
        for j in range(other_axis_size):
            if is_matching(new_bits):
                collapsed_bits.append((i, j))
            new_bits >>= 1

    return collapsed_bits


def wave_function_collapse(blacks: Grid, whites: Grid):
    if blacks.is_solved():
        return "finished"
    # TODO: implement a FUNCTIONAL way to check for squares which cannot be black
    and_1 = lambda x: x & 1
    nand_1 = lambda x: (x & 1) != 0
    collapsed_black_bits = wave_function_collapse_axis(
        blacks.metadata.rows_domain,
        blacks.rows,
        blacks.metadata.col_size,
        operator.and_,
        and_1,
    )

    collapsed_black_bits.extend(
        map(
            lambda x: x[::-1],
            wave_function_collapse_axis(
                blacks.metadata.cols_domain,
                blacks.cols,
                blacks.metadata.row_size,
                operator.and_,
                and_1,
            ),
        )
    )

    # print(f"{len(collapsed_black_bits)} new black squares found")
    for pos in collapsed_black_bits:
        blacks[pos] = True

    collapsed_white_bits = wave_function_collapse_axis(
        whites.metadata.rows_domain,
        whites.rows,
        whites.metadata.col_size,
        operator.or_,
        nand_1,
    )

    collapsed_white_bits.extend(
        map(
            lambda x: x[::-1],
            wave_function_collapse_axis(
                whites.metadata.cols_domain,
                whites.cols,
                whites.metadata.row_size,
                operator.or_,
                nand_1,
            ),
        )
    )
    # print(f"{len(collapsed_white_bits)} new white squares found")
    for pos in collapsed_white_bits:
        whites[pos] = False

    # print(blacks)
    # print("-" * 20)
    # print(whites)
    # print("=" * 20)
    if not collapsed_black_bits and not collapsed_black_bits:
        return "stalemate"
    result = blacks.metadata.reduce_solutions(blacks.rows, blacks.cols, is_black=True)
    if result == "dead end":
        return "wrong answer"
    result = whites.metadata.reduce_solutions(whites.rows, whites.cols, is_black=False)
    if result == "dead end":
        return "wrong answer"
    return "progress"


def collapse_until(blacks, whites):
    while True:
        result = wave_function_collapse(blacks, whites)
        if result != "progress":
            return result


def find_smallest(meta: Board_Metadata) -> list[list[tuple[Point, bool]]]:
    skip_if_solved = lambda x: x if x > 1 else 9999999999
    lenmapr = list(map(skip_if_solved, map(len, meta.rows_domain)))
    lenmapc = list(map(skip_if_solved, map(len, meta.cols_domain)))
    minr = min(lenmapr)
    minc = min(lenmapc)
    if minr <= minc:
        domain = meta.rows_domain
        domain_width = meta.col_size
        order = 1
        idx = lenmapr.index(minr)
        # print("smallest domain on row:", idx, "with", minr, "solutions")
    else:
        domain = meta.cols_domain
        domain_width = meta.row_size
        order = -1
        idx = lenmapc.index(minc)
        # print("smallest domain on col:", idx, "with", minc, "solutions")
    possibe_sols = domain[idx]
    # print(possibe_sols)
    # generate list of moves
    res = []
    for final_state in possibe_sols:
        moves = []

        for i in range(domain_width):
            moves.append(((idx, i)[::order], bool(final_state & 1)))
            final_state >>= 1
        res.append(moves)
    return res


def solve(meta: Board_Metadata):
    times_guessed = 0
    nodes_checked = 1
    base_meta = meta
    # print("row domain sizes: ", list(map(len, meta.rows_domain)))
    # print("col domain sizes: ", list(map(len, meta.cols_domain)))
    # dfs implemented here
    blacks = Grid(meta)
    whites = Grid(meta, inverted=True)
    states = [(blacks.serialize(), whites.serialize())]

    while True:
        if len(states) == 0:
            return "could not be solved"
        b, w = states.pop()
        # print(b)
        cur_meta = deepcopy(base_meta)
        # avoid unsolvable boards
        try:
            blacks.deserialize(b, cur_meta, True)
            whites.deserialize(w, cur_meta, False)
        except ValueError:
            # skipping invalid solution
            continue
        # reduce domain deterministically
        result = collapse_until(blacks, whites)
        b, w = blacks.serialize(), whites.serialize()
        match result:
            case "finished":
                break
            case "stalemate":
                times_guessed += 1
                print(f"{times_guessed=}, {nodes_checked=}")
                p = list(map(len, blacks.metadata.rows_domain))
                q = list(map(len, blacks.metadata.cols_domain))
                print("row domain sizes: ", p)
                print("col domain sizes: ", q)
                print("search space:", sum(p) + sum(q))
                # TODO: profiling needs, remove me!
                if times_guessed >= 30:
                    return
                best_guess = find_smallest(blacks.metadata)
                # reduce domain by trying out all possibilities
                for moves in best_guess:
                    for move, val in moves:
                        blacks[move] = val

                    # res = blacks.metadata.reduce_solutions(blacks.rows, blacks.cols)
                    nodes_checked += 1
                    # try to reduce checking???
                    # if res != "dead end":
                    #     states.append((blacks.serialize(), w))
                    states.append((blacks.serialize(), w))

                    # restore to current
                    blacks.deserialize(b, deepcopy(base_meta), True)
                    # whites.deserialize(w, deepcopy(base_meta), False)

            case "wrong answer":
                # print("wrong answer???")
                # print("unreachable state I think")
                pass

    # print solution
    blacks.sols_to_rows()
    print("soolved!!!!!")
    # print(blacks)
    with open("zad_output.txt", "w") as f:
        f.write(str(blacks))


if __name__ == "__main__":
    # meta = read_input("zad_5_by_5.txt")
    # meta = read_input("zad_input_dummy.txt")
    # print(meta)
    meta = read_input("zad_input.txt")
    if meta is None:
        raise Exception("errors while reading input")
    solve(meta)
    # with cProfile.Profile() as pr:
    #     solve(meta)

    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.dump_stats(filename="nonograms_profiling.prof")
