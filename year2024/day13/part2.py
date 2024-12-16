from typing import cast

from values import values


async def run() -> int:
    result = 0

    machines = values.split_sections("\n\n")

    for machine in machines:
        for row in machine:
            if "Button A" in row:
                button_a = cast(tuple[int, int], row.ints())
            if "Button B" in row:
                button_b = cast(tuple[int, int], row.ints())
            if "Prize" in row:
                prize = cast(tuple[int, int], tuple(v + 10000000000000 for v in row.ints()))

        determinant = button_a[0] * button_b[1] - button_a[1] * button_b[0]
        if determinant == 0:
            continue

        a = (prize[0] * button_b[1] - prize[1] * button_b[0]) / determinant
        b = (button_a[0] * prize[1] - button_a[1] * prize[0]) / determinant

        if a >= 0 and b >= 0 and a.is_integer() and b.is_integer():
            cost = 3 * int(a) + int(b)
            result += cost

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  13
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day13/input
#
# Result: 104140871044942
