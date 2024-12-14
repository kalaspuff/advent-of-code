from helpers import tuple_add
from values import values


async def run() -> int:
    result = 0

    coordinates = [set(values.matrix.pos(str(i))) for i in range(10)]
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))

    for trailhead in coordinates[0]:
        i = 1
        positions = {trailhead}

        while i < 10:
            positions_ = set()
            for pos in positions:
                for mod in dirs:
                    pos_ = tuple_add(pos, mod)
                    if pos_ in coordinates[i]:
                        positions_.add(pos_)

            if not positions_:
                positions = set()
                break

            positions = positions_
            i += 1

        if positions:
            result += len(positions)

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  10
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day10/input
#
# Result: 461
