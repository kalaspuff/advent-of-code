from values import values


async def run() -> int:
    result = 0

    for a, b in values.findall(r"mul[(](\d{1,3}),(\d{1,3})[)]"):
        result += int(a) * int(b)

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  3
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day3/input
#
# Result: 187833789
