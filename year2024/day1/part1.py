from values import values


async def run() -> int:
    left_list = []
    right_list = []

    for row in values.ints():
        left_list.append(row[0])
        right_list.append(row[1])

    return sum(abs(l - r) for l, r in zip(sorted(left_list), sorted(right_list)))


# [values.year]            (number)  2024
# [values.day]             (number)  1
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day1/input
#
# Result: 1882714
