from typing import cast

from values import values


async def run() -> int:
    result = 0

    max_presses = 100
    machines = values.split_sections("\n\n")

    for machine in machines:
        for row in machine:
            if "Button A" in row:
                button_a = cast(tuple[int, int], row.ints())
            if "Button B" in row:
                button_b = cast(tuple[int, int], row.ints())
            if "Prize" in row:
                prize = cast(tuple[int, int], row.ints())

        found = False
        min_cost = float("inf")

        for a in range(max_presses + 1):
            for b in range(max_presses + 1):
                x = a * button_a[0] + b * button_b[0]
                y = a * button_a[1] + b * button_b[1]

                if x == prize[0] and y == prize[1]:
                    found = True
                    cost = 3 * a + b
                    min_cost = min(min_cost, cost)

        if found:
            result += int(min_cost)

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  13
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day13/input
#
# Result: 29201
