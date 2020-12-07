from values import values
from year2019.computer import IntcodeComputer


async def run():
    computer = IntcodeComputer(values)

    for noun in range(0, 100):
        for verb in range(0, 100):
            values.noun = noun
            values.verb = verb

            computer.reset()

            computer.memory[1] = noun
            computer.memory[2] = verb

            computer.run()

            if computer.memory[0] == 19690720:
                return 100 * noun + verb


# [values.year]            (number)  2019
# [values.day]             (number)  2
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2019/day2/input
# [values.noun]            (number)  45
# [values.verb]            (number)  59
#
# Result: 4559
