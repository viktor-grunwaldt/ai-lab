from itertools import product, chain
from more_itertools import flatten, windowed


def range2d(x, y):
    return product(range(x), range(y))


def B(i, j):
    return "B_%d_%d" % (i, j)


def domains(Bs):
    return [q + " in 0..1" for q in Bs]


def sum_cs(Qs, val):
    return f"sum([{', '.join(Qs)}] , #=, {val})"


def get_column(j, col_len):
    return [B(i, j) for i in range(col_len)]


def get_row(i, row_len):
    return [B(i, j) for j in range(row_len)]


def vertical(col_len, sums):
    return [sum_cs(get_column(j, col_len), val) for j, val in enumerate(sums)]


def horizontal(row_len, sums):
    return [sum_cs(get_row(i, row_len), val) for i, val in enumerate(sums)]


#         0
# 0X0 and X are both not possible (min width 2)
#         0
def diff_one(Qs):
    a, b, c = Qs
    return f"{a} + 2*{b} + 4*{c} #\\= 2"


def triplets_axis(elems):
    return [diff_one(points) for points in windowed(elems, 3)]


def triplets(row_len, col_len):
    vert = (triplets_axis(get_row(i, row_len)) for i in range(col_len))
    hor = (triplets_axis(get_column(j, col_len)) for j in range(row_len))
    return list(flatten(chain(vert, hor)))


def triplets_v2(row_len, col_len):
    all_1x3s = list(map(list, chain(*[windowed(get_column(j, col_len), 3) for j in range(row_len)])))
    all_3x1s = list(map(list, chain(*[windowed(get_column(i, row_len), 3) for i in range(col_len)])))
    # all_1x3s = list(chain(map(list, windowed(get_column(j, col_len), 3)) for j in range(row_len)))
    # print(all_1x3s)
    # all_3x1s = [list(windowed(get_row(i, row_len), 3)) for i in range(col_len)]
    legal_tuples = [str(list(t)) for t in product(range(2), repeat=3) if t != (0, 1, 0)]
    body = "tuples_in({}, {})".format(all_1x3s + all_3x1s, legal_tuples).replace("'", "")
    return [body]


def quadruplets(row_len, col_len):
    square = list(range2d(2, 2))

    def shift(sq, pt):
        dx, dy = pt
        return [B(x + dx, y + dy) for x, y in sq]

    all_2x2s = [shift(square, pt) for pt in range2d(col_len - 1, row_len - 1)]
    # illegal tuples
    # XX XX X0 0X X0 0X
    # X0 0X XX XX 0X X0
    # 6 cases, which means 10 cases are legal
    legal_tuples = [
        "[0,0,0,0]",
        "[0,0,0,1]",
        "[0,0,1,0]",
        "[0,1,0,0]",
        "[1,0,0,0]",  # empty and corners
        "[1,1,0,0]",
        "[0,0,1,1]",
        "[0,1,0,1]",
        "[1,0,1,0]",  # 2 if neighbors
        "[1,1,1,1]",  # complete
    ]
    body = "tuples_in({}, {})".format(all_2x2s, legal_tuples).replace("'", "")
    return [body]


def format_constraints(Cs, indent, d) -> str:
    position = indent
    out = [indent * " "]
    for c in Cs:
        out.append(c + ", ")
        position += len(c)
        if position > d:
            position = indent
            out.append("\n" + indent * " ")

    return "".join(out)


def storms(rows, cols, assigments) -> str:
    col_length = len(rows)
    row_length = len(cols)

    variables = [B(i, j) for i, j in range2d(row_length, col_length)]

    out = []
    out.append(":- use_module(library(clpfd)).")
    out.append("solve([" + ", ".join(variables) + "]) :- ")
    cs = (
        domains(variables)
        + horizontal(row_length, rows)
        + vertical(col_length, cols)
        + triplets(row_length, col_length)
        + quadruplets(row_length, col_length)
    )
    # out.append(
    #     "    [%s] = [1,1,0,1,1,0,1,1,0,1,1,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0],"
    #     % (", ".join(variables),)
    # )  # only for test 1
    for i, j, val in assigments:
        cs.append("%s #= %d" % (B(i, j), val))
    out.append(format_constraints(cs, 4, 70))
    out.append("    labeling([ff], [" + ", ".join(variables) + "]).")
    out.append("")
    out.append(":- tell('prolog_result.txt'), solve(X), write(X), nl, told.")
    return "\n".join(out)


if __name__ == "__main__":
    with open("zad_input.txt") as f:
        txt = f.readlines()

    rows = list(map(int, txt[0].split()))
    cols = list(map(int, txt[1].split()))
    triples = []

    for i in range(2, len(txt)):
        if txt[i].strip():
            triples.append(map(int, txt[i].split()))

    res = storms(rows, cols, triples)
    with open("zad_output.txt", "w") as f:
        f.write(res)

"""
SUDOKU OUTPUT
:- use_module(library(clpfd)).
solve([V0_0, V0_1, V0_2, V0_3, V0_4, V0_5, V0_6, V0_7, V0_8, V1_0, V1_1, V1_2, V1_3, V1_4, V1_5, V1_6, V1_7, V1_8, V2_0, V2_1, V2_2, V2_3, V2_4, V2_5, V2_6, V2_7, V2_8, V3_0, V3_1, V3_2, V3_3, V3_4, V3_5, V3_6, V3_7, V3_8, V4_0, V4_1, V4_2, V4_3, V4_4, V4_5, V4_6, V4_7, V4_8, V5_0, V5_1, V5_2, V5_3, V5_4, V5_5, V5_6, V5_7, V5_8, V6_0, V6_1, V6_2, V6_3, V6_4, V6_5, V6_6, V6_7, V6_8, V7_0, V7_1, V7_2, V7_3, V7_4, V7_5, V7_6, V7_7, V7_8, V8_0, V8_1, V8_2, V8_3, V8_4, V8_5, V8_6, V8_7, V8_8]) :- # noqa: E501
    V0_0 in 1..9, V0_1 in 1..9, V0_2 in 1..9, V0_3 in 1..9, V0_4 in 1..9, V0_5 in 1..9,
    V0_6 in 1..9, V0_7 in 1..9, V0_8 in 1..9, V1_0 in 1..9, V1_1 in 1..9, V1_2 in 1..9,
    V1_3 in 1..9, V1_4 in 1..9, V1_5 in 1..9, V1_6 in 1..9, V1_7 in 1..9, V1_8 in 1..9,
    V2_0 in 1..9, V2_1 in 1..9, V2_2 in 1..9, V2_3 in 1..9, V2_4 in 1..9, V2_5 in 1..9,
    V2_6 in 1..9, V2_7 in 1..9, V2_8 in 1..9, V3_0 in 1..9, V3_1 in 1..9, V3_2 in 1..9,
    V3_3 in 1..9, V3_4 in 1..9, V3_5 in 1..9, V3_6 in 1..9, V3_7 in 1..9, V3_8 in 1..9,
    V4_0 in 1..9, V4_1 in 1..9, V4_2 in 1..9, V4_3 in 1..9, V4_4 in 1..9, V4_5 in 1..9,
    V4_6 in 1..9, V4_7 in 1..9, V4_8 in 1..9, V5_0 in 1..9, V5_1 in 1..9, V5_2 in 1..9,
    V5_3 in 1..9, V5_4 in 1..9, V5_5 in 1..9, V5_6 in 1..9, V5_7 in 1..9, V5_8 in 1..9,
    V6_0 in 1..9, V6_1 in 1..9, V6_2 in 1..9, V6_3 in 1..9, V6_4 in 1..9, V6_5 in 1..9,
    V6_6 in 1..9, V6_7 in 1..9, V6_8 in 1..9, V7_0 in 1..9, V7_1 in 1..9, V7_2 in 1..9,
    V7_3 in 1..9, V7_4 in 1..9, V7_5 in 1..9, V7_6 in 1..9, V7_7 in 1..9, V7_8 in 1..9,
    V8_0 in 1..9, V8_1 in 1..9, V8_2 in 1..9, V8_3 in 1..9, V8_4 in 1..9, V8_5 in 1..9,
    V8_6 in 1..9, V8_7 in 1..9, V8_8 in 1..9, all_distinct([V0_0, V1_0, V2_0, V3_0, V4_0, V5_0, V6_0, V7_0, V8_0]),
    all_distinct([V0_1, V1_1, V2_1, V3_1, V4_1, V5_1, V6_1, V7_1, V8_1]),
    all_distinct([V0_2, V1_2, V2_2, V3_2, V4_2, V5_2, V6_2, V7_2, V8_2]),
    all_distinct([V0_3, V1_3, V2_3, V3_3, V4_3, V5_3, V6_3, V7_3, V8_3]),
    all_distinct([V0_4, V1_4, V2_4, V3_4, V4_4, V5_4, V6_4, V7_4, V8_4]),
    all_distinct([V0_5, V1_5, V2_5, V3_5, V4_5, V5_5, V6_5, V7_5, V8_5]),
    all_distinct([V0_6, V1_6, V2_6, V3_6, V4_6, V5_6, V6_6, V7_6, V8_6]),
    all_distinct([V0_7, V1_7, V2_7, V3_7, V4_7, V5_7, V6_7, V7_7, V8_7]),
    all_distinct([V0_8, V1_8, V2_8, V3_8, V4_8, V5_8, V6_8, V7_8, V8_8]),
    all_distinct([V0_0, V0_1, V0_2, V0_3, V0_4, V0_5, V0_6, V0_7, V0_8]),
    all_distinct([V1_0, V1_1, V1_2, V1_3, V1_4, V1_5, V1_6, V1_7, V1_8]),
    all_distinct([V2_0, V2_1, V2_2, V2_3, V2_4, V2_5, V2_6, V2_7, V2_8]),
    all_distinct([V3_0, V3_1, V3_2, V3_3, V3_4, V3_5, V3_6, V3_7, V3_8]),
    all_distinct([V4_0, V4_1, V4_2, V4_3, V4_4, V4_5, V4_6, V4_7, V4_8]),
    all_distinct([V5_0, V5_1, V5_2, V5_3, V5_4, V5_5, V5_6, V5_7, V5_8]),
    all_distinct([V6_0, V6_1, V6_2, V6_3, V6_4, V6_5, V6_6, V6_7, V6_8]),
    all_distinct([V7_0, V7_1, V7_2, V7_3, V7_4, V7_5, V7_6, V7_7, V7_8]),
    all_distinct([V8_0, V8_1, V8_2, V8_3, V8_4, V8_5, V8_6, V8_7, V8_8]),
    all_distinct([V0_0, V0_1, V0_2, V1_0, V1_1, V1_2, V2_0, V2_1, V2_2]),
    all_distinct([V0_3, V0_4, V0_5, V1_3, V1_4, V1_5, V2_3, V2_4, V2_5]),
    all_distinct([V0_6, V0_7, V0_8, V1_6, V1_7, V1_8, V2_6, V2_7, V2_8]),
    all_distinct([V3_0, V3_1, V3_2, V4_0, V4_1, V4_2, V5_0, V5_1, V5_2]),
    all_distinct([V3_3, V3_4, V3_5, V4_3, V4_4, V4_5, V5_3, V5_4, V5_5]),
    all_distinct([V3_6, V3_7, V3_8, V4_6, V4_7, V4_8, V5_6, V5_7, V5_8]),
    all_distinct([V6_0, V6_1, V6_2, V7_0, V7_1, V7_2, V8_0, V8_1, V8_2]),
    all_distinct([V6_3, V6_4, V6_5, V7_3, V7_4, V7_5, V8_3, V8_4, V8_5]),
    all_distinct([V6_6, V6_7, V6_8, V7_6, V7_7, V7_8, V8_6, V8_7, V8_8]),
    V0_0 #= 3, V0_8 #= 1, V1_0 #= 4, V1_3 #= 3, V1_4 #= 8, V1_5 #= 6, V2_5 #= 1, V2_7 #= 4,
    V3_0 #= 6, V3_2 #= 9, V3_3 #= 2, V3_4 #= 4, V3_7 #= 3, V4_2 #= 3, V5_6 #= 7, V5_7 #= 1,
    V5_8 #= 9, V6_8 #= 6, V7_0 #= 2, V7_2 #= 7, V7_6 #= 3,

    labeling([ff], [V0_0, V0_1, V0_2, V0_3, V0_4, V0_5, V0_6, V0_7, V0_8, V1_0, V1_1, V1_2, V1_3, V1_4, V1_5, V1_6, V1_7, V1_8, V2_0, V2_1, V2_2, V2_3, V2_4, V2_5, V2_6, V2_7, V2_8, V3_0, V3_1, V3_2, V3_3, V3_4, V3_5, V3_6, V3_7, V3_8, V4_0, V4_1, V4_2, V4_3, V4_4, V4_5, V4_6, V4_7, V4_8, V5_0, V5_1, V5_2, V5_3, V5_4, V5_5, V5_6, V5_7, V5_8, V6_0, V6_1, V6_2, V6_3, V6_4, V6_5, V6_6, V6_7, V6_8, V7_0, V7_1, V7_2, V7_3, V7_4, V7_5, V7_6, V7_7, V7_8, V8_0, V8_1, V8_2, V8_3, V8_4, V8_5, V8_6, V8_7, V8_8]).

:- solve(X), write(X), nl.
"""
