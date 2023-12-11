import itertools

from helpers import tuple_add
from values import values

START_DIRECTION_MAP = {
    (1, 0): ("-", "J", "7"),
    (0, 1): ("|", "J", "L"),
    (-1, 0): ("-", "L", "F"),
    (0, -1): ("|", "7", "F"),
}

START_PIPE_MAP: dict[frozenset[tuple[int, int]], str] = {
    frozenset({(1, 0), (-1, 0)}): "-",
    frozenset({(0, 1), (0, -1)}): "|",
    frozenset({(1, 0), (0, -1)}): "L",
    frozenset({(1, 0), (0, 1)}): "F",
    frozenset({(0, -1), (-1, 0)}): "J",
    frozenset({(0, 1), (-1, 0)}): "7",
}


async def run() -> int:
    matrix = values.matrix.pad(1, ".")
    start_pos = matrix.pos_first("S")
    if not start_pos:
        raise Exception("No start position found")

    start_directions: set[tuple[int, int]] = set()
    for direction, pipes in START_DIRECTION_MAP.items():
        if matrix[tuple_add(start_pos, direction)] in pipes:
            start_directions.add(direction)

    matrix[start_pos] = START_PIPE_MAP[frozenset(start_directions)]

    direction = start_directions.pop()
    visited_nodes: set[tuple[int, int]] = set()
    position = start_pos
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

    zoomed_matrix = matrix.zoom(coordinates=visited_nodes)
    for pos in visited_nodes:
        pos_ = tuple_add(pos, pos)
        if matrix[pos] in ("-", "L", "F"):
            zoomed_matrix[tuple_add(pos_, (1, 0))] = "-"
        if matrix[pos] in ("|", "7", "F"):
            zoomed_matrix[tuple_add(pos_, (0, 1))] = "|"

    positions: set[tuple[int, int]] = {(0, 0)}
    possible_positions = set(zoomed_matrix.position("."))

    while positions:
        pos = positions.pop()
        possible_positions.remove(pos)
        zoomed_matrix[pos] = "0"
        for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
            pos_ = tuple_add(pos, mod)
            if pos_ in possible_positions:
                positions.add(pos_)

    result_matrix = zoomed_matrix.replace(".", "I").replace("0", ".").zoom_out()
    print(result_matrix)
    return result_matrix.count("I")


# [values.year]            (number)  2023
# [values.day]             (number)  10
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day10/input
#
# Result: 287
