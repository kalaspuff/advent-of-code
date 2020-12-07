from values import values


async def run():
    for value in values.int_rows:
        while True:
            value = int(value / 3) - 2
            if value <= 0:
                break
            values.counter += value

    return values.counter


# [values.year]            (number)  2019
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2019/day1/input
# [values.counter]         (number)  5129386
#
# Result: 5129386
