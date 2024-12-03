from values import values


async def run() -> int:
    result = 0

    mul_enabled = True
    for cmd, a, b in values.findall(r"(mul[(](\d{1,3}),(\d{1,3})[)]|do[(][)]|don't[(][)])"):
        if cmd == "do()":
            mul_enabled = True
        elif cmd == "don't()":
            mul_enabled = False
        elif mul_enabled:
            result += int(a) * int(b)

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  3
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day3/input
#
# Result: 94455185
