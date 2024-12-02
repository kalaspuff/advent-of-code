from helpers import pairwise
from values import values


async def run() -> int:
    result = 0

    for levels in values.ints():
        diffs = [b - a for a, b in pairwise(levels)]
        if (max(diffs) < 0 and min(diffs) >= -3) or (min(diffs) > 0 and max(diffs) <= 3):
            result += 1

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  2
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day2/input
#
# Result: 591
