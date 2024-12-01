from values import values


async def run() -> int:
    left_list = []
    right_list = []

    for row in values.ints():
        left_list.append(row[0])
        right_list.append(row[1])

    return sum(l * right_list.count(l) for l in left_list)


# [values.year]            (number)  2024
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day1/input
#
# Result: 19437052
