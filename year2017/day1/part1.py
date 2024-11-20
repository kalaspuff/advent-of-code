from values import values


async def run() -> int:
    result = 0

    row = str(values[0]) + str(values[0][0])
    for c1, c2 in pairwise(row):
        if c1 == c2:
            result += int(c1)

    return result


# [values.year]            (number)  2017
# [values.day]             (number)  1
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2017/day1/input
#
# Result: 1047
