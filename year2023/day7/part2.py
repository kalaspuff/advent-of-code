import itertools
from collections import Counter

from values import values

CARD_RANKS = "AKQT98765432J"
JOKER = list(CARD_RANKS)


def joker_scored(hand: str) -> tuple[tuple[int, ...], ...]:
    if "J" not in hand:
        return hand_strength(hand, hand)

    possibilities = ([card] if card != "J" else JOKER for card in list(hand))
    max_score = ()
    for hand_ in set(itertools.product(*possibilities)):
        score = hand_strength("".join(hand_), hand)
        if score > max_score:
            max_score = score
    return max_score


def hand_strength(hand: str, actual_hand: str) -> tuple[tuple[int, ...], ...]:
    card_count = Counter(hand).most_common()
    point_ranking = tuple(count for _, count in card_count)
    unsorted_card_ranking = tuple(-CARD_RANKS.index(x) for x in list(actual_hand))
    if point_ranking[0] > 1:
        return (point_ranking, unsorted_card_ranking)
    high_card_ranking = tuple(sorted((-CARD_RANKS.index(x) for x in list(hand)), reverse=True))
    return (point_ranking, unsorted_card_ranking, high_card_ranking)


async def run():
    result = 0

    hands_and_bids = [(hand, bid) for hand, bid in values.match_rows(r"(.*) (\d+)", transform=(str, int))]
    sorted_hands = sorted(hands_and_bids, key=lambda x: joker_scored(x[0]), reverse=False)

    for rank, (hand, bid) in enumerate(sorted_hands, start=1):
        result += rank * bid

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  7
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day7/input
#
# Result: 250665248
