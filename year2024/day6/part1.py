from helpers import tuple_add
from values import values


async def run() -> int:
    pos = values.matrix.pos_first("^")
    obstructions = set(values.matrix.pos("#"))
    coordinates = values.matrix.coordinates.keys()

    direction = (0, -1)
    visited = {pos}

    while (next_pos := tuple_add(pos, direction)) in coordinates:
        if next_pos in obstructions:
            direction = (-direction[1], direction[0])
        else:
            pos = next_pos
            visited.add(pos)

    return len(visited)


# [values.year]            (number)  2024
# [values.day]             (number)  6
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day6/input
#
# Result: 4647
