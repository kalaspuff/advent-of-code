from values import values


async def run() -> int:
    result = 0

    for digits in values.digits():
        result += digits[0] * 10 + digits[-1]

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  1
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day1/input
#
# Result: 56108
