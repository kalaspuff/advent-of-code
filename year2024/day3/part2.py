import re

from values import values


async def run() -> int:
    result = 0

    mul_enabled = True
    for match in re.finditer(r"mul[(](\d+),(\d+)[)]|do[(][)]|don't[(][)]", values.input.replace("\n", "")):
        if match.group(0) == "do()":
            mul_enabled = True
        elif match.group(0) == "don't()":
            mul_enabled = False
        elif mul_enabled:
            a, b = int(match.group(1)), int(match.group(2))
            result += a * b

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  3
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day3/input
#
# Result: 94455185
