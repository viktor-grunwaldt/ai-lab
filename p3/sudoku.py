import itertools


def V(i, j):
    return "V%d_%d" % (i, j)


def domains(Vs):
    return [q + " in 1..9" for q in Vs]


def all_different(Qs):
    return "all_distinct([" + ", ".join(Qs) + "])"


def get_column(j):
    return [V(i, j) for i in range(9)]


def get_row(i):
    return [V(i, j) for j in range(9)]


def get_block(x: int):
    dx, dy = divmod(x, 3)
    return [V(i + 3 * dx, j + 3 * dy) for i, j in itertools.product(range(3), repeat=2)]


def blocks():
    return [all_different(get_block(i)) for i in range(9)]


def horizontal():
    return [all_different(get_row(i)) for i in range(9)]


def vertical():
    return [all_different(get_column(j)) for j in range(9)]


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


def sudoku(assigments):
    variables = [V(i, j) for i in range(9) for j in range(9)]
    out = []
    out.append(":- use_module(library(clpfd)).")
    out.append("solve([" + ", ".join(variables) + "]) :- ")

    cs = (
        domains(variables) + vertical() + horizontal() + blocks()
    )
    for i, j, val in assigments:
        cs.append("%s #= %d" % (V(i, j), val))

    out.append(format_constraints(cs, 4, 70))
    out.append("")
    out.append("    labeling([ff], [" + ", ".join(variables) + "]).")
    out.append("")
    out.append(":- solve(X), write(X), nl.")
    return "\n".join(out)


if __name__ == "__main__":
    raw = 0
    triples = []
    with open("zad_input.txt", "r") as f:
        data = f.readlines()

    for x in data:
        x = x.strip()
        if len(x) == 9:
            for i in range(9):
                if x[i] != ".":
                    triples.append((raw, i, int(x[i])))
            raw += 1
    out = sudoku(triples)
    with open("zad_output.txt", "w") as f:
        f.write(out)


"""
89.356.1.
3...1.49.
....2985.
9.7.6432.
.........
.6389.1.4
.3298....
.78.4....
.5.637.48

53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79

3.......1
4..386...
.....1.4.
6.924..3.
..3......
......719
........6
2.7...3..
"""
