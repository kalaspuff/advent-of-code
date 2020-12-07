from values import values


async def run():
    for value in values.int_rows:
        values.counter += int(value / 3) - 2

    return values.counter


# [values.year]            (number)  2019
# [values.day]             (number)  1
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2019/day1/input
# [values.counter]         (number)  3421505
#
# Result: 3421505
