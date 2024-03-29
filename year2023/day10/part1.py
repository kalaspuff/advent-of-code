from helpers import tuple_add
from values import values


async def run() -> int:
    matrix = values.matrix.pad(1, ".")
    start_pos = matrix.pos_first("S")
    if not start_pos:
        raise Exception("No start position found")

    direction: tuple[int, int]
    if matrix[tuple_add(start_pos, (1, 0))] in ("-", "J", "7"):
        direction = (1, 0)
    elif matrix[tuple_add(start_pos, (0, 1))] in ("|", "J", "L"):
        direction = (0, 1)
    elif matrix[tuple_add(start_pos, (-1, 0))] in ("-", "L", "F"):
        direction = (-1, 0)
    else:
        direction = (0, -1)

    position = start_pos
    visited_nodes: set[tuple[int, int]] = set()
    while position not in visited_nodes:
        visited_nodes.add(position)
        position = tuple_add(position, direction)
        match matrix[position]:
            case "L":
                direction = (1, 0) if direction == (0, 1) else (0, -1)
            case "J":
                direction = (0, -1) if direction == (1, 0) else (-1, 0)
            case "7":
                direction = (-1, 0) if direction == (0, -1) else (0, 1)
            case "F":
                direction = (0, 1) if direction == (-1, 0) else (1, 0)

    return len(visited_nodes) // 2


# [values.year]            (number)  2023
# [values.day]             (number)  10
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day10/input
#
# Result: 6870
