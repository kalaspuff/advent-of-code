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

        boundary = set()
        positions_with_sides = set()
        for pos_ in region:
            for mod in dirs:
                neighbour = tuple_add(pos_, mod)
                if neighbour not in region:
                    boundary.add(neighbour)
                    positions_with_sides.add(pos_)

        left_sides = set()
        right_sides = set()
        top_sides = set()
        bottom_sides = set()
        for pos_ in positions_with_sides:
            neighbour = tuple_add(pos_, (-1, 0))
            if neighbour in boundary:
                left_sides.add(pos_)
            neighbour = tuple_add(pos_, (1, 0))
            if neighbour in boundary:
                right_sides.add(pos_)
            neighbour = tuple_add(pos_, (0, -1))
            if neighbour in boundary:
                top_sides.add(pos_)
            neighbour = tuple_add(pos_, (0, 1))
            if neighbour in boundary:
                bottom_sides.add(pos_)

        sides = 0

        for pos_ in sorted(left_sides):
            sides += 1
            neighbour = tuple_add(pos_, (0, 1))
            if neighbour in left_sides:
                sides -= 1

        for pos_ in sorted(right_sides):
            sides += 1
            neighbour = tuple_add(pos_, (0, 1))
            if neighbour in right_sides:
                sides -= 1

        for pos_ in sorted(top_sides):
            sides += 1
            neighbour = tuple_add(pos_, (1, 0))
            if neighbour in top_sides:
                sides -= 1

        for pos_ in sorted(bottom_sides):
            sides += 1
            neighbour = tuple_add(pos_, (1, 0))
            if neighbour in bottom_sides:
                sides -= 1

        area = len(region)
        result += area * sides

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  12
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day12/input
#
# Result: 865662
