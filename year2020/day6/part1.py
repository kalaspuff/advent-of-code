from values import values


async def run():
    for rows in values.grouped_rows():
        questions = set("".join(rows))
        values.result.append(len(questions))

    return sum(values.result)


# [values.year]            (number)  2020
# [values.day]             (number)  6
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2020/day6/input
# [values.result]          (list)    [4, 24, 3, 12, 18, 23, 1, 20, ...]
#
# Result: 6387
