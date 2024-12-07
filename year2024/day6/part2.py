from typing import cast

from helpers import tuple_add
from values import values


class LoopDetectedError(Exception):
    pass


def simulate_path(
    pos: tuple[int, int], obstructions: set[tuple[int, int]], coordinates: set[tuple[int, int]]
) -> tuple[tuple[int, int], ...]:
    direction = (0, -1)
    visited: set[tuple[tuple[int, int], tuple[int, int]]] = {(pos, direction)}

    while (next_pos := tuple_add(pos, direction)) in coordinates:
        if next_pos in obstructions:
            direction = (-direction[1], direction[0])
        elif (next_pos, direction) in visited:
            raise LoopDetectedError
        else:
            pos = next_pos
            visited.add((pos, direction))

    return tuple(p for p, _ in visited)


async def run() -> int:
    result = 0

    start_pos = cast(tuple[int, int], values.matrix.pos_first("^"))
    obstructions = set(values.matrix.pos("#"))
    coordinates = set(values.matrix.coordinates.keys())
    path_positions = set(simulate_path(start_pos, obstructions, coordinates))

    for obstruction_pos in path_positions:
        try:
            simulate_path(start_pos, obstructions | {obstruction_pos}, coordinates)
        except LoopDetectedError:
            result += 1

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  6
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day6/input
#
# Result: 1723
