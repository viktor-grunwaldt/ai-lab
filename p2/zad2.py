import collections
import numpy as np


def transfer_to_game_state(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace("\n", "") for x in layout]
    layout = [",".join(layout[i]) for i in range(len(layout))]
    layout = [x.split(",") for x in layout]
    max_cols_len = max([len(x) for x in layout])
    layout_trans = ".WKBG*"
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            layout[irow][icol] = layout_trans.index(layout[irow][icol])

        cols_len = len(layout[irow])
        if cols_len < max_cols_len:
            layout[irow].extend([1 for _ in range(max_cols_len - cols_len)])
    return np.array(layout)


def pos_player(game_state):
    """Return the position of agent"""
    return tuple(np.argwhere(game_state == 2)[0])  # e.g. (2, 2)


def pos_box(game_state):
    """Return the positions of boxes"""
    return tuple(
        tuple(x) for x in np.argwhere((game_state == 3) | (game_state == 5))
    )  # e.g. ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))


def pos_walls(game_state):
    """Return the positions of walls"""
    return tuple(
        tuple(x) for x in np.argwhere(game_state == 1)
    )  # e.g. like those above


def pos_goals(game_state):
    """Return the positions of goals"""
    return tuple(
        tuple(x) for x in np.argwhere((game_state == 4) | (game_state == 5))
    )  # e.g. like those above


def is_end_state(box_pos):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(box_pos) == sorted(goals_pos)


def is_legal_action(action, player_pos, box_pos):
    """Check if the given action is legal"""
    x_player, y_player = player_pos
    if action[-1].isupper():  # the move was a push
        x1, y1 = x_player + 2 * action[0], y_player + 2 * action[1]
    else:
        x1, y1 = x_player + action[0], y_player + action[1]
    return (x1, y1) not in box_pos + walls_pos


def legal_actions(player_pos, box_pos):
    """Return all legal actions for the agent in the current game state"""
    all_actions = [
        [-1, 0, "u", "U"],
        [1, 0, "d", "D"],
        [0, -1, "l", "L"],
        [0, 1, "r", "R"],
    ]
    x_player, y_player = player_pos
    legal_actions = []
    for action in all_actions:
        x1, y1 = x_player + action[0], y_player + action[1]
        if (x1, y1) in box_pos:  # the move was a push
            action.pop(2)  # drop the little letter
        else:
            action.pop(3)  # drop the upper letter
        if is_legal_action(action, player_pos, box_pos):
            legal_actions.append(action)
        else:
            continue
    return tuple(tuple(x) for x in legal_actions)  # e.g. ((0, -1, 'l'), (0, 1, 'R'))


def update_state(player_pos, box_pos, action):
    """Return updated game state after an action is taken"""
    x_player, y_player = player_pos  # the previous position of player
    newplayer_pos = [
        x_player + action[0],
        y_player + action[1],
    ]  # the current position of player
    box_pos = [list(x) for x in box_pos]
    if action[-1].isupper():  # if pushing, update the position of box
        box_pos.remove(newplayer_pos)
        box_pos.append([x_player + 2 * action[0], y_player + 2 * action[1]])
    box_pos = tuple(tuple(x) for x in box_pos)
    newplayer_pos = tuple(newplayer_pos)
    return newplayer_pos, box_pos


def is_failed(box_pos):
    """This function used to observe if the state is potentially failed, then prune the search"""
    rotatePattern = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [2, 5, 8, 1, 4, 7, 0, 3, 6],
        [0, 1, 2, 3, 4, 5, 6, 7, 8][::-1],
        [2, 5, 8, 1, 4, 7, 0, 3, 6][::-1],
    ]
    flipPattern = [
        [2, 1, 0, 5, 4, 3, 8, 7, 6],
        [0, 3, 6, 1, 4, 7, 2, 5, 8],
        [2, 1, 0, 5, 4, 3, 8, 7, 6][::-1],
        [0, 3, 6, 1, 4, 7, 2, 5, 8][::-1],
    ]
    allPattern = rotatePattern + flipPattern

    for box in box_pos:
        if box not in goals_pos:
            board = [
                (box[0] - 1, box[1] - 1),
                (box[0] - 1, box[1]),
                (box[0] - 1, box[1] + 1),
                (box[0], box[1] - 1),
                (box[0], box[1]),
                (box[0], box[1] + 1),
                (box[0] + 1, box[1] - 1),
                (box[0] + 1, box[1]),
                (box[0] + 1, box[1] + 1),
            ]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in walls_pos and newBoard[5] in walls_pos:
                    return True
                elif (
                    newBoard[1] in box_pos
                    and newBoard[2] in walls_pos
                    and newBoard[5] in walls_pos
                ):
                    return True
                elif (
                    newBoard[1] in box_pos
                    and newBoard[2] in walls_pos
                    and newBoard[5] in box_pos
                ):
                    return True
                elif (
                    newBoard[1] in box_pos
                    and newBoard[2] in box_pos
                    and newBoard[5] in box_pos
                ):
                    return True
                elif (
                    newBoard[1] in box_pos
                    and newBoard[6] in box_pos
                    and newBoard[2] in walls_pos
                    and newBoard[3] in walls_pos
                    and newBoard[8] in walls_pos
                ):
                    return True
    return False


def bfs():
    begin_box = pos_box(game_state)
    begin_player = pos_player(game_state)

    startState = (
        begin_player,
        begin_box,
    )  # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5)))
    to_visit = collections.deque([[startState]])  # store states
    actions = collections.deque([[0]])  # store actions
    visited = set()
    while to_visit:
        node = to_visit.popleft()
        node_action = actions.popleft()
        if is_end_state(node[-1][-1]):
            return "".join(node_action[1:]).upper()
        if node[-1] not in visited:
            visited.add(node[-1])
            for action in legal_actions(node[-1][0], node[-1][1]):
                newplayer_pos, newbox_pos = update_state(
                    node[-1][0], node[-1][1], action
                )
                if is_failed(newbox_pos):
                    continue
                to_visit.append(node + [(newplayer_pos, newbox_pos)])
                actions.append(node_action + [action[-1]])

    return "not found"


def read():
    with open("zad_input.txt", "r") as f:
        layout = f.readlines()

    return layout


if __name__ == "__main__":
    layout = read()
    game_state = transfer_to_game_state(layout)
    walls_pos = pos_walls(game_state)
    goals_pos = pos_goals(game_state)

    actions = bfs()
    with open("zad_output.txt", "w") as outf:
        outf.write(actions)
