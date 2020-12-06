from helpers import tuple_sum
from values import values


async def run():
    matrix = values.matrix.options(infinite_x=True)

    chars = []
    pos = 0, 0
    move = 3, 1

    try:
        while True:
            pos = tuple_sum(pos, move)
            chars.append(matrix[pos])
    except IndexError:
        pass

    return chars.count("#")


# [values.year]            (number)  2020
# [values.day]             (number)  3
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2020/day3/input
#
# Result: 181
