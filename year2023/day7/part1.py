from collections import Counter

from values import values

CARD_RANKS = "AKQJT98765432"


def hand_strength(hand: str) -> tuple[tuple[int, ...], ...]:
    card_count = Counter(hand).most_common()
    point_ranking = tuple(count for _, count in card_count)
    unsorted_card_ranking = tuple(-CARD_RANKS.index(x) for x in list(hand))
    if point_ranking[0] > 1:
        return (point_ranking, unsorted_card_ranking)
    high_card_ranking = tuple(sorted(unsorted_card_ranking, reverse=True))
    return (point_ranking, unsorted_card_ranking, high_card_ranking)


async def run() -> int:
    result = 0

    hands_and_bids = [(hand, bid) for hand, bid in values.match_rows(r"(.*) (\d+)", transform=(str, int))]
    sorted_hands = sorted(hands_and_bids, key=lambda x: hand_strength(x[0]), reverse=False)

    for rank, (hand, bid) in enumerate(sorted_hands, start=1):
        result += rank * bid

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  7
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day7/input
#
# Result: 250120186
