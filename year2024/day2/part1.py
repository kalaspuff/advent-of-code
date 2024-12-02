from helpers import pairwise
from values import values


async def run() -> int:
    result = 0

    for levels in values.ints():
        if levels != tuple(sorted(levels)) and levels != tuple(sorted(levels, reverse=True)):
            continue

        if all(1 <= abs(a - b) <= 3 for a, b in pairwise(sorted(levels))):
            result += 1

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  2
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day2/input
#
# Result: 591
