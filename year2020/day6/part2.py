from values import values


async def run():
    for rows in values.grouped_rows():
        questions = set("".join(rows))
        for row in rows:
            questions = questions & set(row)
        values.result.append(len(questions))

    return sum(values.result)


# [values.year]            (number)  2020
# [values.day]             (number)  6
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2020/day6/input
# [values.result]          (list)    [0, 15, 3, 7, 6, 18, 1, 17, ...]
#
# Result: 3039
