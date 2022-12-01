from values import values


async def run():
    last_value = None
    increases = 0
    for v in values.int_rows:
        if last_value is not None and v > last_value:
            increases += 1
        last_value = v
    return increases


# [values.year]            (number)  2021
# [values.day]             (number)  1
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2021/day1/input
#
# Result: 1451
