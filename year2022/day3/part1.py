from values import values


async def run():
    mapping = dict([t[::-1] for t in enumerate(list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"), 1)])

    prios = []
    for row in values.rows:
        item_count = len(row)
        c1, c2 = row[0 : item_count // 2], row[item_count // 2 :]
        prios.append(mapping[(set(list(c1)) & set(list(c2))).pop()])

    return sum(prios)


# [values.year]            (number)  2022
# [values.day]             (number)  3
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day3/input
#
# Result: 8298
