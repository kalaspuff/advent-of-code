from helpers import tuple_add
from values import values

DIRECTIONS: dict[str, tuple[int, int]] = {
    "R": (1, 0),
    "D": (0, 1),
    "L": (-1, 0),
    "U": (0, -1),
}


async def run() -> int:
    area = 0
    edge_length = 0
    pos = (0, 0)

    parse_direction = lambda v: DIRECTIONS[v]
    for direction, distance, _ in values.match_rows(
        r"^([RDLU])\s+(\d+)\s+[(][#]([0-9a-f]+)[)]", transform=(parse_direction, int, str)
    ):
        pos_ = tuple_add(pos, (direction[0] * distance, direction[1] * distance))
        edge_length += distance
        area += pos[0] * pos_[1] - pos_[0] * pos[1]

        pos = pos_

    return (area - edge_length) // 2 + edge_length + 1


# [values.year]            (number)  2023
# [values.day]             (number)  18
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day18/input
#
# Result: 50603
