from helpers import tuple_add
from values import values

DIRECTIONS: dict[str, tuple[int, int]] = {
    "3": (0, -1),
    "1": (0, 1),
    "2": (-1, 0),
    "0": (1, 0),
}


async def run() -> int:
    area = 0
    edge_length = 0
    pos = (0, 0)

    parse_direction = lambda v: DIRECTIONS[v]
    parse_distance = lambda v: int(v, 16)

    for distance, direction in values.match_rows(
        r"[RLUD]\s+\d+\s+[(][#]([0-9a-f]{5})([0-3])[)]", transform=(parse_distance, parse_direction)
    ):
        pos_ = tuple_add(pos, (direction[0] * distance, direction[1] * distance))
        edge_length += distance
        area += pos[0] * pos_[1] - pos_[0] * pos[1]

        pos = pos_

    return (area - edge_length) // 2 + edge_length + 1


# [values.year]            (number)  2023
# [values.day]             (number)  0
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day0/input
#
# Result: 50603
