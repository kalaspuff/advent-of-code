from values import values


async def run():
    mapping = dict([t[::-1] for t in enumerate(list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"), 1)])
    grouped_rows = [values.rows[i:i + 3] for i in range(0, len(values.rows), 3)]

    prios = []
    for rows in grouped_rows:
        prios.append(mapping[(set(list(rows[0])) & set(list(rows[1])) & set(list(rows[2]))).pop()])

    return sum(prios)


# [values.year]            (number)  2022
# [values.day]             (number)  3
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day3/input
#
# Result: 2708
