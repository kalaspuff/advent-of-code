from values import values
from year2019.computer import IntcodeComputer


async def run():
    computer = IntcodeComputer(values)
    computer.run(5)

    return computer.output[0]


# [values.year]            (number)  2019
# [values.day]             (number)  5
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2019/day5/input
#
# Result: 4655956
