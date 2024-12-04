import itertools

from helpers import tuple_add
from values import values


async def run() -> int:
    result = 0

    letters = "XMAS"
    positions: dict[str, set[tuple[int, int]]] = {}

    for letter in letters:
        positions[letter] = {pos for pos in values.matrix.pos(letter)}

    for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
        for pos in positions[letters[0]]:
            pos_ = pos
            for letter in letters[1:]:
                pos_ = tuple_add(pos_, mod)
                if pos_ not in positions[letter]:
                    break
            else:
                result += 1

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  4
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day4/input
#
# Result: 2571
