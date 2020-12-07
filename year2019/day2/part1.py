from values import values
from year2019.computer import IntcodeComputer


async def run():
    computer = IntcodeComputer(values)

    computer.memory[1] = 12
    computer.memory[2] = 2

    computer.run()

    return computer.memory[0]


# [values.year]            (number)  2019
# [values.day]             (number)  2
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2019/day2/input
#
# Result: 5434663
