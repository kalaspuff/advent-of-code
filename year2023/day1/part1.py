from values import values


async def run():
    result = 0

    for row in values.rows:
        digits = [c for c in row if c.isdigit()]
        result += int(str(digits[0]) + str(digits[-1]))

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  1
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day1/input
#
# Result: 56108
