from typing import cast

from helpers import tuple_add
from values import values


async def run() -> int:
    start_pos = cast(tuple[int, int], values.matrix.pos_first("^"))
    obstructions = set(values.matrix.pos("#"))
    coordinates = values.matrix.coordinates.keys()

    pos = start_pos
    direction: tuple[int, int] = (0, -1)
    simulated_positions = set()

    while True:
        next_pos = tuple_add(pos, direction)

        if next_pos not in coordinates:
            break

        if next_pos in obstructions:
            direction = (-direction[1], direction[0])
        else:
            pos = next_pos
            simulated_positions.add(pos)

    potential_obstructions = set()

    for obstruction_pos in simulated_positions:
        pos = start_pos
        direction = (0, -1)
        visited_dirs: set[tuple[tuple[int, int], tuple[int, int]]] = {(pos, direction)}
        obstructions_ = obstructions | {obstruction_pos}

        while True:
            next_pos = tuple_add(pos, direction)

            if next_pos not in coordinates:
                break

            if next_pos in obstructions_:
                direction = (-direction[1], direction[0])
            else:
                if (next_pos, direction) in visited_dirs:
                    potential_obstructions.add(obstruction_pos)
                    break

                pos = next_pos
                visited_dirs.add((pos, direction))

    return len(potential_obstructions)


# [values.year]            (number)  2024
# [values.day]             (number)  6
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day6/input
#
# Result: 1723
