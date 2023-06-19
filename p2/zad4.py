"""
"######################\n"
"#SSSSSSSS#SSS##SSSSSS#\n"
"#SSSSSSSSSSSS##SSSSSS#\n"
"#SSSSSS###SSSSSSSSS#B#\n"
"#SSSSSS###SSSSSSSSSSS#\n"
"#SSSSSSSSSSSSSSSSSSSS#\n"
"#####SSSSSSSSSSSSSSSS#\n"
"#SSSSSSSSSSSSSSSSSSSS#\n"
"######################\n"
"""
from collections import deque
from copy import deepcopy
from dataclasses import dataclass

Pair = tuple[int, int]


@dataclass
class Board:
    grid: list[list[str]]
    positions: set[Pair]
    goals: list[Pair]
    walls: set[Pair]


def print_grid(grid: list[list[str]], positions: set[Pair]):
    canvas = deepcopy(grid)
    for i, j in positions:
        canvas[i][j] = "C"

    print("\n".join("".join(row) for row in canvas))
    print("-" * 30)


def read_input():
    with open("zad_input.txt", "r") as f:
        data = f.read()
    grid = [[*line] for line in data.splitlines()]
    goals = []
    positions = []
    walls = []
    for i, row in enumerate(grid):
        for j, x in enumerate(row):
            match x:
                case "B" | "G":
                    goals.append((i, j))
                case "S":
                    positions.append((i, j))
                    grid[i][j] = " "
                case "#":
                    walls.append((i, j))

    return Board(grid, set(positions), goals, set(walls))


# hard limit of 150 moves
moves_vert = [1, 0, -1, 0]
moves_hor = [0, 1, 0, -1]


def addt(a: Pair, b: Pair):
    return (a[0] + b[0], a[1] + b[1])


# assume pos is legal. then there will be no out of bounds
def no_collision(pos: Pair, dirs: Pair, grid: list[list[str]]) -> bool:
    x, y = addt(pos, dirs)
    return grid[x][y] != "#"


def move(pos: Pair, dirs: Pair, grid: list[list[str]]) -> Pair:
    return addt(pos, dirs) if no_collision(pos, dirs, grid) else pos


def reducing_move(wall_pos: Pair, dx, dy, b: Board):
    wx, wy = wall_pos
    return (wx - dx, wy - dy) in b.positions and (
        wx - 2 * dx,
        wy - 2 * dy,
    ) in b.positions or any(goal in b.positions for goal in b.goals)


def reduce_positions(b: Board, move_limit: int):
    # for each direction, count how many positions will be reduced
    # maybe look ahead when reducing moves?
    b.positions = set(b.positions)
    moves = []
    # like this: dir = E
    # #SS
    # after = #S
    # recuced = 1
    # which means if S is -dir and -2dir, then it will reduce
    for _ in range(move_limit):
        # if only one is left, it's trivial
        if len(b.positions) <= 1:
            return moves

        pos_values = []
        for dx, dy in zip(moves_hor, moves_vert):
            counter = sum(1 for ws in b.walls if reducing_move(ws, dx, dy, b))
            pos_values.append(counter)

        best_idx = pos_values.index(max(pos_values))
        if all(i == 0 for i in pos_values):
            # do a bfs to reduce
            print("yikes, nontrivial situation")

            break

        moves.append("URDL"[best_idx])
        # moving part
        dirs = (moves_hor[best_idx], moves_vert[best_idx])

        new_pos_set = set(move(pos, dirs, b.grid) for pos in b.positions)

        b.positions = new_pos_set

    return moves


MOVE_DIR = {
    (1, 0): "U",
    (0, 1): "R",
    (-1, 0): "D",
    (0, -1): "L",
}


def backtrack_path(visited: dict, current: tuple[Pair], path=[]):
    match visited.get(current):
        case None:
            print(visited)
            raise Exception
        case prev, (0, 0):
            return path
        case prev, pmove:
            path.append(MOVE_DIR.get(pmove))
            return backtrack_path(visited, prev, path)
        case anyhow:
            raise Exception("unreachable state" + str(current))


# state = all positions + last move
# goal = reducing move or move limit hit
# solution = moves
# edges = allowed moves which don't repeat
# visited stores parent state + edge
def bfs_for_reducing_move(b: Board):
    if len(b.positions) == 1:
        return []

    visited: dict = {}
    to_visit: deque[tuple[tuple[Pair], tuple[Pair], Pair]] = deque()
    to_visit.append((tuple(b.positions), None, (0, 0)))
    solved = None

    while to_visit:
        current, prev, prevmove = to_visit.popleft()
        visited[current] = (prev, prevmove)
        if len(current) != len(set(current)):
            solved = current
            break
        for dxy in zip(moves_hor, moves_vert):
            next = tuple(move(pos, dxy, b.grid) for pos in current)
            if next not in visited and next != current:
                to_visit.append((next, current, dxy))

    if solved is not None:
        # impl finding path
        b.positions = set(current)
        return backtrack_path(visited, solved) + [MOVE_DIR[prevmove]]
    else:
        raise Exception("nothing found, get a better programmer")


def bfs_to_targets(b: Board):
    visited: dict = {}
    to_visit: deque[Pair] = deque()
    pos = list(b.positions)[0]
    to_visit.append((pos, None, (0, 0)))
    solved = None

    while to_visit:
        pos, prev, prevmove = to_visit.popleft()
        visited[pos] = (prev, prevmove)
        if pos in b.goals:
            solved = pos
            break

        for dxy in zip(moves_hor, moves_vert):
            next = move(pos, dxy, b.grid)
            if next not in visited and next != pos:
                to_visit.append((next, pos, dxy))


def bfs_to_targets_parrallel(b: Board):
    visited: dict = {}
    to_visit: deque[Pair] = deque()
    pos = tuple(b.positions)
    to_visit.append((pos, None, (0, 0)))
    solved = None

    while to_visit:
        print(len(visited))
        pos, prev, prevmove = to_visit.popleft()
        visited[pos] = (prev, prevmove)
        if len(set(pos)) < len(pos):
            print("reduced count")
            pos = tuple(set(pos))
        for p in pos:
            if p in b.goals:
                print("found a goal")
                pos = tuple(x for x in pos if x != p)
                solved = (p,)
        if not pos:
            break
        for dxy in zip(moves_hor, moves_vert):
            next = tuple(move(p, dxy, b.grid) for p in pos)
            if next not in visited and next != pos:
                to_visit.append((next, pos, dxy))

    if solved is not None:
        # impl finding path
        b.positions = set(solved)
        # b.goals.remove(pos)
        return backtrack_path(visited, solved) + list(prevmove)
    else:
        raise Exception("nothing found, get a better programmer")


if __name__ == "__main__":
    m = []
    b = read_input()
    while len(b.positions) > 3:
        m.extend(reduce_positions(b, 20))
        old_len = len(m)
        m.extend(bfs_for_reducing_move(b))
        new_len = len(m)

    if len(m) > 150:
        print("fail")

    m.extend(bfs_to_targets_parrallel(b))
    print(m)
    print("".join(m))
    with open("zad_output.txt", "w") as f:
        f.write("".join(m))
