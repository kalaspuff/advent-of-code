from values import values


async def run():
    result = 0

    parse_numbers = lambda n: set(map(int, n.split()))
    for winning_numbers, my_numbers in values.findall_rows(r"[:|]\s+((?:\d+\s*)+)", transform=parse_numbers):
        matches = len(winning_numbers & my_numbers)
        if matches:
            result += 2 ** (matches - 1)

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  4
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day4/input
#
# Result: 23847
