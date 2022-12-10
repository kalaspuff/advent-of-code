from values import values


async def run():
    stack = []

    for instruction, value in values.match_rows(r"^([a-z]+)(?:\s+([0-9-]+))?$", (str, str)):
        if instruction == "noop":
            stack.insert(0, (lambda r: r,))
        elif instruction == "addx":
            stack.insert(0, (lambda r: r,))
            stack.insert(0, (lambda r, v: {**r, "X": r["X"] + v}, int(value)))

    registers = {"X": 1}
    cycle = 0
    signal_strength = 0
    while stack:
        cycle += 1
        if (cycle + 20) % 40 == 0:
            signal_strength += registers["X"] * cycle
        func, *args = stack.pop()
        registers = func(registers, *args)

    return signal_strength


# [values.year]            (number)  2022
# [values.day]             (number)  10
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day0/input
#
# Result: 13760
