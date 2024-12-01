from values import values


async def run() -> int:
    return values.input.count("(") - values.input.count(")")


# [values.year]            (number)  2016
# [values.day]             (number)  1
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2016/day1/input
#
# Result: 74
