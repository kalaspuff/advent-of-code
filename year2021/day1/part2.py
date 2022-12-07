from values import values


async def run():
    last_value = None
    increases = 0
    for i in range(len(values.int_rows)):
        v = sum(values.int_rows[i : (i + 3)])
        if last_value is not None and v > last_value:
            increases += 1
        last_value = v
    return increases


# [values.year]            (number)  2021
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2021/day1/input
#
# Result: 1395
