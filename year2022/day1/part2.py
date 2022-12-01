from values import values


async def run():
    elves = list(sorted([(sum(map(int, v)), i) for i, v in enumerate(values.grouped_rows())], reverse=True))
    return sum([v for v, i in elves[0:3]])


# [values.year]            (number)  2022
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day1/input
#
# Result: 202346
