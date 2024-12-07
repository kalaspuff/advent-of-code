import itertools

from helpers import paired
from values import values


async def run() -> int:
    result = 0

    for test_value, *numbers in values.ints():
        op_count = len(numbers) - 1
        calculations = set()
        for operators in itertools.product(*(("+", "*"),) * op_count):
            calculation = list(map(str, numbers[:]))
            for calc_idx, op in zip(range(1, len(numbers) * 2, 2), operators):
                calculation.insert(calc_idx, op)

            # calculations.add(eval("".join(calculation)))

            value = int(calculation[0])
            for op, next_value in paired(calculation[1:]):
                if op == "+":
                    value += int(next_value)
                elif op == "*":
                    value *= int(next_value)

            calculations.add(value)

        if test_value in calculations:
            result += test_value

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  7
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day7/input
#
# Result: 1153997401072
