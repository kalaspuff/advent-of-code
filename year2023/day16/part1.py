from helpers import tuple_add
from values import values


async def run() -> int:
    matrix = values.matrix
    range_x, range_y = range(matrix.width), range(matrix.height)

    beams: set[tuple[tuple[int, int], tuple[int, int]]] = {((-1, 0), (1, 0))}
    visited_positions = set()
    all_beams: set[tuple[tuple[int, int], tuple[int, int]]] = set()

    while beams:
        pos, direction = beams.pop()

        if (pos, direction) in all_beams:
            continue

        all_beams.add((pos, direction))
        pos_ = tuple_add(pos, direction)

        if pos[0] in range_x and pos[1] in range_y:
            visited_positions.add(pos)

        if pos_[0] not in range_x or pos_[1] not in range_y:
            continue

        match matrix[pos_]:
            case "|" if direction[1] == 0:
                beams.add((pos_, (0, 1)))
                beams.add((pos_, (0, -1)))
            case "-" if direction[0] == 0:
                beams.add((pos_, (1, 0)))
                beams.add((pos_, (-1, 0)))
            case "\\" if direction == (1, 0):
                beams.add((pos_, (0, 1)))
            case "\\" if direction == (-1, 0):
                beams.add((pos_, (0, -1)))
            case "\\" if direction == (0, 1):
                beams.add((pos_, (1, 0)))
            case "\\" if direction == (0, -1):
                beams.add((pos_, (-1, 0)))
            case "/" if direction == (1, 0):
                beams.add((pos_, (0, -1)))
            case "/" if direction == (-1, 0):
                beams.add((pos_, (0, 1)))
            case "/" if direction == (0, 1):
                beams.add((pos_, (-1, 0)))
            case "/" if direction == (0, -1):
                beams.add((pos_, (1, 0)))
            case _:
                beams.add((pos_, direction))

    return len(visited_positions)


# [values.year]            (number)  2023
# [values.day]             (number)  16
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day16/input
#
# Result: 6795
