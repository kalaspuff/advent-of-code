from values import values


async def run():
    elves = list(sorted([(sum(map(int, v)), i) for i, v in enumerate(values.grouped_rows())], reverse=True))
    return elves[0][0]


# [values.year]            (number)  2022
# [values.day]             (number)  1
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day1/input
#
# Result: 69501
