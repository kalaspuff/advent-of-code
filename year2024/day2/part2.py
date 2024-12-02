from helpers import pairwise
from values import values


async def run() -> int:
    result = 0

    for levels_ in values.ints():
        for idx in range(len(levels_)):
            levels = levels_[:idx] + levels_[idx + 1 :]
            diffs = [b - a for a, b in pairwise(levels)]
            if (max(diffs) < 0 and min(diffs) >= -3) or (min(diffs) > 0 and max(diffs) <= 3):
                result += 1
                break

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  2
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day2/input
#
# Result: 621
