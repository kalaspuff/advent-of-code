import itertools
import math

from values import values


async def run():
    for p in itertools.permutations(values.int_rows, 3):
        if sum(p) == 2020:
            return math.prod(p)


# [values.year]            (number)  2020
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2020/day1/input
#
# Result: 116115990
