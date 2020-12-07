from helpers import tuple_add
from values import values


async def run():
    positions = {}
    central_port = 0, 0
    intersections = set()

    for wire_id, row in enumerate(values.rows):
        path = row.split(",")
        pos = central_port
        steps = 0
        for p in path:
            direction = p[0]
            length = int(p[1:])
            pos_mod = {"U": (0, -1), "R": (1, 0), "D": (0, 1), "L": (-1, 0)}[direction]
            for _ in range(1, length + 1):
                pos = tuple_add(pos, pos_mod)
                steps += 1
                if pos == central_port:
                    continue
                if pos in positions and positions[pos][0] != wire_id:
                    intersections.add((steps + positions[pos][1], pos))
                else:
                    positions[pos] = (wire_id, steps)

    return min(intersections)[0]


# [values.year]            (number)  2019
# [values.day]             (number)  3
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2019/day3/input
#
# Result: 27890
