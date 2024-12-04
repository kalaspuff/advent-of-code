import itertools

from helpers import tuple_sum
from values import values


async def run() -> int:
    result = 0

    x_pos = set(values.matrix.pos("X"))
    m_pos = set(values.matrix.pos("M"))
    a_pos = set(values.matrix.pos("A"))
    s_pos = set(values.matrix.pos("S"))

    for pos in x_pos:
        for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
            for i, pos_ in enumerate((m_pos, a_pos, s_pos), 1):
                if tuple_sum(pos, *((mod,) * i)) not in pos_:
                    break
            else:
                result += 1

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  4
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day4/input
#
# Result: 2571
