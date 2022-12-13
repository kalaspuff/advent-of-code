import functools
import operator
from typing import List

from values import values


def cmp(*args: List) -> int:
    return functools.reduce(
        lambda a, b: a or b,
        [
            cmp(*map(lambda v: [v, [v]][isinstance(v, int)], pair))
            if list in map(type, pair)
            else cmp(*map(lambda i: [[]] * i, pair))
            for pair in zip(*args)
        ]
        + [0],
    ) or max(min(1, operator.sub(*map(len, args))), -1)


async def run() -> int:
    results = []
    for idx, pair in enumerate(values.grouped_rows(), 1):
        if cmp(*map(eval, pair)) <= 0:
            results.append(idx)

    return sum(results)


# [values.year]            (number)  2022
# [values.day]             (number)  13
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day13/input
#
# Result: 5350
