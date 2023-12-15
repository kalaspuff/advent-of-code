from values import values


async def run() -> int:
    result = 0

    for sequence in values.flatten().split(","):
        current = 0
        for char in sequence:
            current = (current + ord(char)) * 17 % 256
        result += current

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  15
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day1/input
#
# Result: 511215
