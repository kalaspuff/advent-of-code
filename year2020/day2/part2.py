from helpers import int_minus
from values import values


async def run():
    for pos_1, pos_2, char, password in values.match_rows(r"^([0-9]+)-([0-9]+) (.): (.*)$", (int_minus, int_minus)):
        if bool(password[pos_1] == char) ^ bool(password[pos_2] == char):
            values.counter += 1

    return values.counter


# [values.year]            (number)  2020
# [values.day]             (number)  2
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2020/day2/input
# [values.counter]         (number)  267
#
# Result: 267
