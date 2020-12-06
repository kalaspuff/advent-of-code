import math

from helpers import tuple_sum
from values import values


async def run():
    matrix = values.matrix.options(infinite_x=True)

    for move in [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]:
        chars = []
        pos = 0, 0

        try:
            while True:
                pos = tuple_sum(pos, move)
                chars.append(matrix[pos])
        except IndexError:
            pass

        values.result.append(chars.count("#"))

    return math.prod(values.result)


# [values.year]            (number)  2020
# [values.day]             (number)  3
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2020/day3/input
# [values.result]          (list)    [63, 181, 55, 67, 30]
#
# Result: 1260601650
