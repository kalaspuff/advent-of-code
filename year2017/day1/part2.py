from values import values


async def run() -> int:
    result = 0

    row = str(values[0])
    circular_row = row * 2
    for i, c1 in enumerate(row):
        c2 = circular_row[i + len(row) // 2]
        if c1 == c2:
            result += int(c1)

    return result


# [values.year]            (number)  2017
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2017/day1/input
#
# Result: 982
