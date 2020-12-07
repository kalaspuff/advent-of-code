from helpers import tuple_add, manhattan_distance
from matrix import Matrix
from values import values


async def run():
    positions = {}
    central_port = 0, 0
    intersections = set()

    for wire_id, row in enumerate(values.rows):
        path = row.split(",")
        pos = central_port
        for p in path:
            direction = p[0]
            length = int(p[1:])
            pos_mod = {"U": (0, -1), "R": (1, 0), "D": (0, 1), "L": (-1, 0)}[direction]
            for _ in range(1, length + 1):
                pos = tuple_add(pos, pos_mod)
                if pos == central_port:
                    continue
                if pos in positions and positions[pos] != wire_id:
                    intersections.add((manhattan_distance(pos, central_port), pos))
                else:
                    positions[pos] = wire_id

    return min(intersections)[0]


# [values.year]            (number)  2019
# [values.day]             (number)  3
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2019/day3/input
#
# Result: 2427
