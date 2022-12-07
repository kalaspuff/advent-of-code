from values import values


async def run():
    count = 14
    for i in range(len(values.input_)):
        if len(set(list(values.input_[i : i + count]))) == count:
            return i + count


# [values.year]            (number)  2022
# [values.day]             (number)  6
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day6/input
#
# Result: 2202
