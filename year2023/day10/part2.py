import itertools

from helpers import tuple_add
from matrix import Matrix
from values import values


async def run() -> int:
    matrix = Matrix(["."] + [f".{row}." for row in values.rows] + ["."], width=len(values[0]) + 2, fill=".")
    start_pos = matrix.pos_first("S")

    start_direction_map = {
        (1, 0): ("-", "J", "7"),
        (0, 1): ("|", "J", "L"),
        (-1, 0): ("-", "L", "F"),
        (0, -1): ("|", "7", "F"),
    }
    start_pipe_map = {
        frozenset({(1, 0), (-1, 0)}): "-",
        frozenset({(0, 1), (0, -1)}): "|",
        frozenset({(1, 0), (0, -1)}): "L",
        frozenset({(1, 0), (0, 1)}): "F",
        frozenset({(0, -1), (-1, 0)}): "J",
        frozenset({(0, 1), (-1, 0)}): "7",
    }

    start_directions = set()
    for direction, pipes in start_direction_map.items():
        if matrix[tuple_add(start_pos, direction)] in pipes:
            start_directions.add(direction)

    matrix[start_pos] = start_pipe_map[frozenset(start_directions)]

    direction = start_directions.pop()
    visited_nodes = set()
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

    zoomed_matrix = Matrix(None, 2 + matrix.width * 2, 2 + matrix.height * 2, fill=".")
    for pos in visited_nodes:
        if pos not in visited_nodes:
            continue
        pos_ = tuple_add(tuple_add(pos, pos), (2, 2))
        zoomed_matrix[pos_] = matrix[pos]
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
        if pos >= (2, 2) and pos[0] % 2 == 0 and pos[1] % 2 == 0:
            x, y = pos
            matrix[pos[0] // 2 - 1, pos[1] // 2 - 1] = "."
        for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
            pos_ = tuple_add(pos, mod)
            if pos_ in possible_positions:
                positions.add(pos_)

    enclosed_position_count = 0
    for x in range(0, zoomed_matrix.width, 2):
        for y in range(0, zoomed_matrix.height, 2):
            if zoomed_matrix[x, y] == ".":
                matrix[(x // 2) - 1, (y // 2) - 1] = "I"
                enclosed_position_count += 1

    print(matrix)

    return enclosed_position_count


# [values.year]            (number)  2023
# [values.day]             (number)  10
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day10/input
#
# Result: 287
