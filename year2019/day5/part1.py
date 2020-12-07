from values import values
from year2019.computer import IntcodeComputer


async def run():
    computer = IntcodeComputer(values)

    def output_function(value):
        if value == 0:
            print(f"* computer output: {value} | {computer} ")

    values.computer_output = computer.output
    computer.output_function = output_function
    computer.run(1)

    print()
    values.tests_output = computer.output[0:-1]
    values.successs_count = values.tests_output.count(0)
    values.failed_count = len(values.tests_output) - values.tests_output.count(0)

    if any(list(values.tests_output)):
        return "error"

    return computer.output[-1]


# * computer output: 0 | <IntcodeComputer state="RUNNING" ops=3 pointer=10 current=Opcode.OUTPUT>
# * computer output: 0 | <IntcodeComputer state="RUNNING" ops=9 pointer=32 current=Opcode.OUTPUT>
# * computer output: 0 | <IntcodeComputer state="RUNNING" ops=15 pointer=54 current=Opcode.OUTPUT>
# * computer output: 0 | <IntcodeComputer state="RUNNING" ops=22 pointer=80 current=Opcode.OUTPUT>
# * computer output: 0 | <IntcodeComputer state="RUNNING" ops=29 pointer=106 current=Opcode.OUTPUT>
# * computer output: 0 | <IntcodeComputer state="RUNNING" ops=37 pointer=136 current=Opcode.OUTPUT>
# * computer output: 0 | <IntcodeComputer state="RUNNING" ops=43 pointer=158 current=Opcode.OUTPUT>
# * computer output: 0 | <IntcodeComputer state="RUNNING" ops=50 pointer=184 current=Opcode.OUTPUT>
# * computer output: 0 | <IntcodeComputer state="RUNNING" ops=56 pointer=206 current=Opcode.OUTPUT>
#
# [values.year]            (number)  2019
# [values.day]             (number)  5
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2019/day5/input
# [values.computer_output] (list)    [0, 0, 0, 0, 0, 0, 0, 0, 0, 14522484]
# [values.tests_output]    (list)    [0, 0, 0, 0, 0, 0, 0, 0, 0]
# [values.successs_count]  (number)  9
# [values.failed_count]    (number)  0
#
# Result: 14522484
