from values import values


async def run() -> int:
    result = 0

    for i, char in enumerate(values.input, start=1):
        if char == "(":
            result += 1
        elif char == ")":
            result -= 1
            if result == -1:
                return i

    raise ValueError("No basement found")


# [values.year]            (number)  2016
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2015/day1/input
#
# Result: 1795
