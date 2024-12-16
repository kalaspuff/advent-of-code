from helpers import tuple_add
from values import values


async def run() -> int:
    result = 0

    dirs = ((0, 1), (0, -1), (1, 0), (-1, 0))
    visited = set()
    for pos, plant in values.matrix.coordinates.items():
        if pos in visited:
            continue

        plant_coordinates = set(values.matrix.pos(plant))
        region = set()
        neighbours = {pos}
        perimeter = 0

        while neighbours:
            pos_ = neighbours.pop()
            if pos_ in visited:
                continue

            visited.add(pos_)
            region.add(pos_)

            for mod in dirs:
                neighbour = tuple_add(pos_, mod)
                if neighbour in plant_coordinates:
                    neighbours.add(neighbour)
                else:
                    perimeter += 1

        area = len(region)
        result += area * perimeter

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  12
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day12/input
#
# Result: 1450816
