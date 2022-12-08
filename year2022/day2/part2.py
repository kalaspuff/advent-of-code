import functools
from values import values


async def run():
    mapping = {
        "A Y": 3 + 2,
        "B Z": 6 + 3,
        "C X": 0 + 1,
        "A X": 0 + 2,
        "B Y": 3 + 3,
        "C Z": 6 + 1,
        "A Z": 6 + 2,
        "B X": 0 + 3,
        "C Y": 3 + 1,
    }

    return sum([mapping[row] for row in values.rows])


# [values.year]            (number)  2022
# [values.day]             (number)  2
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day2/input
#
# Result: 11998
