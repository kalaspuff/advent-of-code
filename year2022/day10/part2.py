from matrix import Matrix
from values import values


async def run():
    stack = []

    for instruction, value in values.match_rows(r"^([a-z]+)(?:\s+([0-9-]+))?$", (str, str)):
        if instruction == "noop":
            stack.insert(0, (lambda r: r,))
        elif instruction == "addx":
            stack.insert(0, (lambda r: r,))
            stack.insert(0, (lambda r, v: {**r, "X": r["X"] + v}, int(value)))

    screen = Matrix(None, width=40, height=6, fill=".")
    registers = {"X": 1}
    cycle = 0
    while stack:
        y = cycle // 40
        x = cycle % 40
        cycle += 1
        if registers["X"] in (x - 1, x, x + 1):
            screen[x, y] = "#"
        func, *args = stack.pop()
        registers = func(registers, *args)

    screen.draw()


# [values.year]            (number)  2022
# [values.day]             (number)  10
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day0/input
#
# Result: RFKZCPEF
