import functools
import itertools
import math

from values import values


async def run():
    matrix = values.matrix
    scores = []

    score_reducer = lambda a, b: a + (([int(b)] if int(b) < max(a) else [-1]) if -1 not in a else [])
    scenic_score_func = lambda l, v: len(functools.reduce(score_reducer, l, [v])) - 1

    for x, y in itertools.product(range(1, matrix.height - 1), range(1, matrix.width - 1)):
        value = int(matrix.get(x, y))

        scores.append(math.prod([
            scenic_score_func(matrix.y(y).rows[0][x + 1:], value),
            scenic_score_func(reversed(matrix.y(y).rows[0][:x]), value),
            scenic_score_func(matrix.x(x).flip.rows[0][y + 1:], value),
            scenic_score_func(reversed(matrix.x(x).flip.rows[0][:y]), value),
        ]))

    return max(scores)


# [values.year]            (number)  2022
# [values.day]             (number)  8
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day8/input
#
# Result: 172224
