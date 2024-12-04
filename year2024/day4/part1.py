import itertools

from helpers import tuple_sum
from values import values


async def run() -> int:
    result = 0

    letter_positions = [set(values.matrix.pos(c)) for c in "XMAS"]

    for pos in letter_positions[0]:
        for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
            for i, pos_ in enumerate(letter_positions[1:], 1):
                if tuple_sum(pos, *((mod,) * i)) not in pos_:
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
