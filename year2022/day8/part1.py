import itertools

from values import values


async def run():
    matrix = values.matrix
    result = matrix.width * 2 + matrix.height * 2 - 4

    for x, y in itertools.product(range(1, matrix.height - 1), range(1, matrix.width - 1)):
        value = int(matrix.get(x, y))
        if not all([
            list(itertools.dropwhile(lambda v: int(v) < value, matrix.y(y).rows[0][x + 1:])),
            list(itertools.dropwhile(lambda v: int(v) < value, matrix.y(y).rows[0][:x])),
            list(itertools.dropwhile(lambda v: int(v) < value, matrix.x(x).flip.rows[0][y + 1:])),
            list(itertools.dropwhile(lambda v: int(v) < value, matrix.x(x).flip.rows[0][:y])),
        ]):
            result += 1

    return result


# [values.year]            (number)  2022
# [values.day]             (number)  8
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day8/input
#
# Result: 1779
