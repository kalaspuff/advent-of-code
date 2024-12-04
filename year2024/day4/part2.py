import itertools

from helpers import tuple_add, tuple_sub
from values import values


async def run() -> int:
    result = 0

    m_pos = set(values.matrix.pos("M"))
    a_pos = set(values.matrix.pos("A"))
    s_pos = set(values.matrix.pos("S"))

    for pos in a_pos:
        matches = 0

        for mod in itertools.product([-1, 1], [-1, 1]):
            if tuple_add(pos, mod) in m_pos and tuple_sub(pos, mod) in s_pos:
                matches += 1

        if matches == 2:
            result += 1

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  4
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day4/input
#
# Result: 1992
