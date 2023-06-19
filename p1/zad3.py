import itertools as it
from collections import defaultdict as dd, Counter
import math

figures = "JQKA"
numerals = "23456789t"
suits = "♠♣♦♥"
fig_id = dict(zip(numerals + figures, range(99)))
col_id = dict(zip(suits, range(9)))
# blotka = spot card]
# figura = figure
unique_flopper_hands_count = math.comb(4 * 9, 5)
unique_highroller_hands_count = math.comb(4 * 4, 5)


def check_hand(hand: list[str]) -> int:
    fig_count = [0] * 13
    col_count = [0] * 4
    for fig, col in map(tuple, hand):
        fig_count[fig_id[fig]] += 1
        col_count[col_id[col]] += 1
    # fig_count.sort(reverse=True)
    # check multiples
    match sorted(fig_count, reverse=True)[:2]:
        case 4, 1:
            return 9
        case 3, 2:
            return 8
        case 3, 1:
            return 5
        case 2, 2:
            return 4
        case 2, 1:
            return 3
        case _:
            # check straight
            sequence_len = max(sum(1 for _ in grps) for k, grps in it.groupby(fig_count) if k == 1)

    match sequence_len, max(col_count):
        case 5, 5:
            return 10
        case 5, _:
            return 6
        case _, 5:
            return 7
        case _:
            return 2


assert check_hand(["9♠", "t♠", "t♦", "J♠", "Q♠"]) == 3
assert check_hand(["8♠", "9♠", "t♠", "J♠", "Q♠"]) == 10


highroller_deck = [f + c for f, c in it.product(figures, suits)]
flopper_deck = [f + c for f, c in it.product(numerals, suits)]


def count_hands(deck: list[str]) -> list[int]:
    possible_hands_count = Counter(map(check_hand, it.combinations(deck, 5)))
    sol = [0] * 11
    for val, count in possible_hands_count.items():
        sol[val] = count

    return sol


def calc_chance_to_win(highroller_deck, flopper_deck) -> str:
    highroller_handtypes_count = count_hands(highroller_deck)
    flopper_handtypes_count = count_hands(flopper_deck)

    # 1_646_701_056

    total_games = unique_flopper_hands_count * unique_highroller_hands_count
    highroller_wins = 0
    for i, val in enumerate(highroller_handtypes_count):
        highroller_wins += val * sum(flopper_handtypes_count[: i + 1])

    return "szansa Blotkarza na wygranie: {}".format((total_games - highroller_wins) / total_games * 100)


# szansa(highroller_deck, flopper_deck)
for i in range(9):
    new_flopper_deck = flopper_deck[i*2:]
    print("rozmiar talli blotkarza:", len(new_flopper_deck))
    print(calc_chance_to_win(highroller_deck, new_flopper_deck))
# ans = count_hands(flopper_deck + highroller_deck)
# print(ans)
# total_hands = math.comb(52, 5)
# print(["{:6f}".format(i*100 / total_hands) for i in ans])

"""
low_win_possibility = 0

for i in range(2, 11):
    sum_of_high_hands = 0
for j in range(2, i):
    sum_of_high_hands += fig_hands[j]
low_win_possibility += low_hands[i] * sum_of_high_hands
"""
