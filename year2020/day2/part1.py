from values import values


async def run():
    for min_, max_, char, password in values.match_rows(r"^([0-9]+)-([0-9]+) (.): (.*)$", (int, int)):
        count = password.count(char)
        if max_ >= count >= min_:
            values.counter += 1

    return values.counter


# [values.year]            (number)  2020
# [values.day]             (number)  2
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2020/day2/input
# [values.counter]         (number)  469
#
# Result: 469
