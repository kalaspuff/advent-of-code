import itertools

from values import values


async def run() -> int:
    result = 0

    for test_value, *numbers in values.ints():
        op_count = len(numbers) - 1
        for operators in itertools.product(*(("+", "*", "||"),) * op_count):
            value = numbers[0]
            for op, next_value in zip(operators, numbers[1:]):
                if op == "+":
                    value += next_value
                elif op == "*":
                    value *= next_value
                elif op == "||":
                    value = int(str(value) + str(next_value))

            if value == test_value:
                result += test_value
                break

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  7
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day7/input
#
# Result: 97902809384118
