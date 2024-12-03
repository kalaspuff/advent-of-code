import re

from values import values


async def run() -> int:
    result = 0

    content = values.input.replace("\n", "")

    for match in re.finditer(r"mul[(](\d+),(\d+)[)]", content):
        a, b = int(match.group(1)), int(match.group(2))
        result += a * b

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  3
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day3/input
#
# Result: 187833789
