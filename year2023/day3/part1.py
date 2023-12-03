import itertools

from helpers import tuple_add
from values import values


def extract_full_number(pos):
    row = values.matrix.y(pos[1])
    boundary = [pos] * 2

    for index, range_ in enumerate([range(pos[0], -1, -1), range(pos[0], row.width, 1)]):
        for x in range_:
            if not str(row.x(x)).isdigit():
                break
            boundary[index] = (x, pos[1])

    number = int(str(row.x(boundary[0][0], boundary[1][0])))
    return tuple(boundary), number


def extract_adjacent_numbers(pos):
    numbers = set()
    for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
        search_pos = tuple_add(pos, mod)
        if str(values.matrix.xy(*search_pos)).isdigit():
            numbers.add(extract_full_number(search_pos))
    return numbers


async def run():
    part_numbers = set()

    for pos, char in values.matrix.coordinates.items():
        if not (char.isdigit() or char == "."):
            extracted_numbers = extract_adjacent_numbers(pos)
            part_numbers |= extracted_numbers

    return sum(part[1] for part in part_numbers)


# [values.year]            (number)  2023
# [values.day]             (number)  3
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day3/input
#
# Result: 530849
