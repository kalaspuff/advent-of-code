from collections import deque

from values import values


async def run():
    result = 0
    originals = []

    parse_numbers = lambda n: set(map(int, n.split()))
    for index, (winning_numbers, my_numbers) in enumerate(
        values.findall_rows(r"[:|]\s+((?:\d+\s*)+)", transform=(parse_numbers, parse_numbers))
    ):
        matches = len(winning_numbers & my_numbers)
        originals.append((index, matches))

    cards = deque(originals)
    while cards:
        index, matches = cards.popleft()
        result += 1
        for details in originals[index + 1 : index + 1 + matches]:
            cards.append(details)

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  4
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day4/input
#
# Result: 8570000
