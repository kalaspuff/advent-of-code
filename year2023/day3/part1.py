import itertools

from helpers import tuple_add
from values import values


def extract_full_number(pos: tuple[int, int]) -> tuple[tuple[int, int], int]:
    row = str(values.matrix.y(pos[1]))
    begin = list(itertools.takewhile(str.isdigit, row[pos[0] - 1 :: -1]))[::-1]
    end = list(itertools.takewhile(str.isdigit, row[pos[0] :: 1]))
    return (pos[0] - len(begin), pos[1]), int("".join(begin + end))


def extract_adjacent_numbers(pos: tuple[int, int]) -> set[tuple[tuple[int, int], int]]:
    numbers = set()
    for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
        search_pos = tuple_add(pos, mod)
        if str(values.matrix.xy(*search_pos)).isdigit():
            numbers.add(extract_full_number(search_pos))
    return numbers


async def run() -> int:
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
