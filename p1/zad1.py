# from dataclasses import dataclass
from itertools import pairwise
from string import ascii_lowercase as s_al
from collections import deque

# from time import sleep


# 4 bits to encode the piece and its color
class Piece:
    Empty = 0
    King = 1
    Rook = 3
    White = 4
    Black = 8

    def make_piece(color: int, fig: int):
        return color | fig


# @dataclass
# class Move:
#     start_square: int
#     end_square: int
#     piece: int


DIRECTION_OFFSETS = (8, -8, 1, -1, 7, -7, 9, -9)
NUM_SQUARES_TO_EDGE = [
    (
        7 - row,
        row,
        7 - col,
        col,
    )
    for row in range(8)
    for col in range(8)
]
"""
     7  8  9
    -1  0  1
    -9 -8 -7
"""

EDGE_DIR = [
    (-8, 1, -1, -7, -9),  # touching up
    (8, 1, -1, 7, 9),  # touching down
    (8, -8, -1, 7, -9),  # touching right side
    (-8, -8, 1, -7, 9),  # touching left
]

CORNER_DIR = {
    0: (1, 8, 9),
    7: (-1, 7, 8),
    56: (-8, -7, 1),
    63: (-9, -8, -1),
}

KING_MOVES = [
    DIRECTION_OFFSETS
    if 0 not in NUM_SQUARES_TO_EDGE[i]
    else EDGE_DIR[NUM_SQUARES_TO_EDGE[i].index(0)]
    if i not in {0, 7, 56, 63}
    else CORNER_DIR[i]
    for i in range(64)
]

ASCII_PIECES = {
    Piece.White | Piece.King: "♔",
    Piece.White | Piece.Rook: "♖",
    Piece.Black | Piece.King: "♚",
    0: "*",
}


class Board:
    color_to_move: int
    white_king: int
    white_rook: int
    black_king: int
    is_check: bool | None

    def __init__(self, init_str: str | None = None, init_board_pos: int | None = None) -> None:
        """example init_str: black g8 h1 c4"""
        self.is_check = None
        if init_str:
            col, wk, wr, bk = init_str.split()
            self.color_to_move = Piece.White if col == "white" else Piece.Black
            self.white_king = Board.pos_from_str(wk)
            self.white_rook = Board.pos_from_str(wr)
            self.black_king = Board.pos_from_str(bk)
        elif init_board_pos:
            self.load_snapshot(init_board_pos)

    # STATIC FUNCTIONS
    def pos_from_str(x):
        return (ord(x[0]) - ord("a")) + (int(x[1]) - 1) * 8

    def from_pos(pos: int) -> str:
        return f"{s_al[pos % 8]}{pos // 8 + 1}"

    def change_snapshot(snapshot: int, piece: Piece, target: int) -> int:
        match piece:
            case 5:  # Piece.make_piece(Piece.White | Piece.King):
                shift = 12
            case 7:  # Piece.make_piece(Piece.White | Piece.Rook):
                shift = 6
            case 9:  # Piece.make_piece(Piece.Black | Piece.King):
                shift = 0
            case _:
                raise ValueError("unknown piece: {}".format(piece))
        # zero out piece's old position
        snapshot &= ~(63 << shift)
        # add new pos
        snapshot += target << shift
        # update whose turn
        snapshot ^= 12 << 18
        return snapshot

    def make_snapshot(self) -> int:
        # converting piece positions to
        return (
            (self.color_to_move << 18)
            + (self.white_king << 12)
            + (self.white_rook << 6)
            + self.black_king
        )

    def move_to_str(begin_pos: int, end_pos: int) -> str:
        return Board.from_pos(begin_pos) + Board.from_pos(end_pos)

    def load_snapshot(self, init_board_pos: int) -> int:
        # reading chunks of bits from snapshot number
        self.black_king = init_board_pos & 63
        self.white_rook = (init_board_pos & (63 << 6)) >> 6
        self.white_king = (init_board_pos & (63 << 12)) >> 12
        self.color_to_move = init_board_pos >> 18

    def __str__(self) -> str:
        ans = " ".join(map(Board.from_pos, (self.white_king, self.white_rook, self.black_king)))
        col = "white" if self.color_to_move == Piece.White else "black"
        return col + " " + ans

    # function for humans
    def ascii(self, markers: list[int] = []) -> str:
        piece_dict = {
            self.white_king: Piece.White | Piece.King,
            self.white_rook: Piece.White | Piece.Rook,
            self.black_king: Piece.Black | Piece.King,
        }
        for m in markers:
            if m not in piece_dict:
                piece_dict[m] = 0

        b = [None] * 8
        for row in range(8):
            line = str(row + 1) + " | "
            for col in range(8):
                if row * 8 + col in piece_dict:
                    line += "{0}{1}{0}".format(
                        "▒" if (col + row) % 2 == 1 else " ",
                        ASCII_PIECES[piece_dict[row * 8 + col]],
                    )
                else:
                    line += 3 * ("▒" if (col + row) % 2 == 1 else " ")

            b[7 - row] = line
        b.append("     a  b  c  d  e  f  g  h ")
        return "\n".join(b)

    def eval_check(self):
        if self.is_check is None:
            self.generate_moves_white_rook()

        return self.is_check

    def generate_moves_black_king(self):
        # moves possible on empty board
        moves: list[int] = [self.black_king + move for move in KING_MOVES[self.black_king]]
        # restricted moves
        rmoves_k = {self.white_king + move for move in KING_MOVES[self.white_king]}
        # just because rook cannot move behind black king it doesn't mean he's safe there
        # TODO: add logic to deny rook from x-raying white king
        row_begin = self.white_rook - self.white_rook % 8
        rmoves_r = set(range(row_begin, row_begin + 8)) | set(range(self.white_rook % 8, 64, 8))
        # legal moves
        return [move for move in moves if move not in rmoves_r and move not in rmoves_k]

    def generate_moves_white_rook(self):
        # we take up, down, right, left up to the egde of the board
        moves = []
        for index_dir, dir_vector in enumerate(DIRECTION_OFFSETS[:4]):
            for i in range(NUM_SQUARES_TO_EDGE[self.white_rook][index_dir]):
                target = self.white_rook + (i + 1) * dir_vector
                # collison detection
                if self.white_king == target:
                    break
                moves.append(target)
                # check
                if self.black_king == target:
                    self.is_check = True
                    break

        if self.is_check is None:
            self.is_check = False
        return moves

    def generate_moves_white_king(self):
        moves = [self.white_king + move for move in KING_MOVES[self.white_king]]
        rmoves = {self.black_king + move for move in KING_MOVES[self.black_king]} | {
            self.black_king,
            self.white_rook,
        }
        return [move for move in moves if move not in rmoves]

    def generate_future_states(self):
        make_states = lambda piece, moves: deque(
            Board.change_snapshot(cur, piece, move) for move in moves
        )
        cur = self.make_snapshot()
        if self.color_to_move == Piece.Black:
            states = make_states(Piece.Black | Piece.King, self.generate_moves_black_king())
        elif self.color_to_move == Piece.White:
            states = make_states(Piece.White | Piece.King, self.generate_moves_white_king())
            states.extend(make_states(Piece.White | Piece.Rook, self.generate_moves_white_rook()))
        else:
            raise Exception("invalid color")
        return states


def diff_in_list(lst1: list[str], lst2: list[str]) -> str:
    return next((l, r) for l, r in zip(lst1, lst2) if l != r)


def solve(input_str) -> str:
    b = Board(init_str=input_str)
    # check for stalemate
    if b.color_to_move == Piece.Black:
        if not b.generate_moves_black_king():
            return "INF"

    visited: dict[int, int] = {b.make_snapshot(): 0}
    to_visit: deque[int] = deque()
    to_visit.append(b.make_snapshot())
    sol_found = None
    while to_visit:
        current_state = to_visit.popleft()
        current_board = Board(init_board_pos=current_state)
        # print(current_board.ascii())
        future_states = current_board.generate_future_states()
        # have we reached end?
        if current_board.eval_check() and not future_states:
            if b.white_rook not in KING_MOVES[b.black_king]:
                sol_found = current_state
                break
        # add all futures to check
        for state in future_states:
            if state in visited:
                continue

            to_visit.append(state)
            visited[state] = current_state

    if sol_found is None:
        raise Exception("how did we even get here?????")

    def find_path(end, visited, path: deque = deque()):
        match visited[end]:
            case 0:
                return path
            case node:
                path.appendleft(node)
                return find_path(node, visited, path)

    snapshots = find_path(sol_found, visited, deque([sol_found]))
    boards_strs = [Board(init_board_pos=snap) for snap in snapshots]
    # print(b.ascii())
    # shows boards
    # for b in boards_strs:
    #     print(b.ascii(b.generate_moves_black_king()))
    lists_strs = [str(b).split()[1:] for b in boards_strs]
    moves = [diff_in_list(pos_pre, pos_post) for pos_pre, pos_post in pairwise(lists_strs)]
    return " ".join(a + b for a, b in moves)


def main(validator_mode: bool = False):
    if not validator_mode:
        print(solve(input()))
    else:
        raise NotImplementedError


# main()
print(solve("white e3 h5 e1"))
