import functools
import operator

from values import values


def cmp(*args):
    for pair in list(zip(*args)):
        if (
            retval := cmp(*map(lambda x: [x] if isinstance(x, int) else x, pair))
            if list in map(type, pair)
            else cmp(*map(lambda x: [[]] * x, pair))
        ):
            return retval
    return max(min(1, operator.sub(*map(len, args))), -1)


async def run():
    divider1 = [[2]]
    divider2 = [[6]]

    rows = [eval(row) for row in values.rows if row] + [divider1, divider2]
    sorted_rows = [[]] + sorted(rows, key=functools.cmp_to_key(cmp))
    return (sorted_rows.index(divider1)) * (sorted_rows.index(divider2))


# [values.year]            (number)  2022
# [values.day]             (number)  13
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day13/input
#
# Result: 19570
