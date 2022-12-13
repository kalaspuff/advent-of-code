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
