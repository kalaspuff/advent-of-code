from values import values


async def run():
    result = 0

    for a1, a2, b1, b2 in values.match_rows(r"(\d+)-(\d+),(\d+)-(\d+)", (int, )):
        ax = set(range(int(a1), int(a2) + 1))
        bx = set(range(int(b1), int(b2) + 1))
        overlap = ax & bx
        if overlap == ax or overlap == bx:
            result += 1

    return result


# [values.year]            (number)  2022
# [values.day]             (number)  4
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day4/input
#
# Result: 588
