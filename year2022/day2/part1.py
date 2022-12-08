from values import values


async def run():
    mapping = {
        "A Y": 6 + 2,
        "B Z": 6 + 3,
        "C X": 6 + 1,
        "A X": 3 + 1,
        "B Y": 3 + 2,
        "C Z": 3 + 3,
        "A Z": 0 + 3,
        "B X": 0 + 1,
        "C Y": 0 + 2,
    }

    return sum([mapping[row] for row in values.rows])


# [values.year]            (number)  2022
# [values.day]             (number)  2
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day2/input
#
# Result: 8933
