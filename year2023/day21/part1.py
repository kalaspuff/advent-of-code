from helpers import tuple_add
from values import values

# (x, y) - right, down, left, up
DIRECTIONS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))


async def run() -> int:
    pos = start_pos = values.matrix.position("S")[0]
    matrix = values.matrix.replace("S", ".")
    possible_positions = set(matrix.position("."))
    max_steps = 64

    queue = {(start_pos, 0)}
    visited = set()

    while queue:
        pos, steps = queue.pop()
        visited.add((pos, steps))

        if steps >= max_steps:
            continue

        for mod in DIRECTIONS:
            pos_ = tuple_add(pos, mod)
            if pos_ not in possible_positions:
                continue

            key = (pos_, steps + 1)
            if key in visited:
                continue

            queue.add(key)

    for pos, steps in visited:
        if steps == max_steps:
            matrix[pos] = "O"

    print(matrix)

    return matrix.count("O")


# [values.year]            (number)  2023
# [values.day]             (number)  21
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day21/input
#
# Result: 3677
