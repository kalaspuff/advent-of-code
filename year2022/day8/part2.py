import functools
import math

from values import values


async def run():
    matrix = values.matrix
    results = []

    score_reducer = lambda a, b: a + (([b] if b < max(a) else [-1]) if -1 not in a else [])
    scenic_score_func = lambda l, v: len(functools.reduce(score_reducer, l, [v])[1:])

    for y in range(matrix.height):
        horizontal_row = list(map(int, matrix.y(y).rows[0]))
        for x in range(matrix.width):
            value = horizontal_row[x]
            vertical_row = list(map(int, matrix.x(x).flip.rows[0]))

            results.append(math.prod([
                scenic_score_func(horizontal_row[x + 1:], value),
                scenic_score_func(reversed(horizontal_row[:x]), value),
                scenic_score_func(vertical_row[y + 1:], value),
                scenic_score_func(reversed(vertical_row[:y]), value),
            ]))

    return max(results)


# [values.year]            (number)  2022
# [values.day]             (number)  8
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day8/input
#
# Result: 172224
