from values import values


async def run() -> int:
    left = [l for l, _ in values.ints()]
    right = [r for _, r in values.ints()]

    return sum(l * right.count(l) for l in left)


# [values.year]            (number)  2024
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day1/input
#
# Result: 19437052
