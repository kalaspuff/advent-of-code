from values import values


async def run() -> int:
    result = 0

    for _, winning_numbers, my_numbers in values.split_values([":", "|"]):
        matches = len(set(winning_numbers.ints()) & set(my_numbers.ints()))
        if matches:
            result += 2 ** (matches - 1)

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  4
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day4/input
#
# Result: 23847
