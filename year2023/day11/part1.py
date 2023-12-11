import itertools

from helpers import manhattan_distance
from values import values


async def run() -> int:
    result = 0

    multi = 2
    rows_without_galaxies = [i for i, row in enumerate(values) if "#" not in row]
    cols_without_galaxies = [i for i, row in enumerate(values.rotate()) if "#" not in row]

    galaxies = values.matrix.position("#")
    for pair in itertools.combinations(galaxies, 2):
        from_, to_ = pair
        extra_x = sum(multi - 1 if from_[0] < n < to_[0] or to_[0] < n < from_[0] else 0 for n in cols_without_galaxies)
        extra_y = sum(multi - 1 if from_[1] < n < to_[1] or to_[1] < n < from_[1] else 0 for n in rows_without_galaxies)
        result += manhattan_distance(from_, to_) + (extra_x + extra_y)

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  11
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day11/input
#
# Result: 9521550
