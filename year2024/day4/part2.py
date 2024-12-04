import itertools

from helpers import tuple_add
from values import values

DIRECTIONS = itertools.product([-1, 1], [-1, 1])


async def run() -> int:
    result = 0

    letters = "MAS"
    positions: dict[str, set[tuple[int, int]]] = {}
    x_mas_positions: list[tuple[int, int]] = []

    for letter in letters:
        positions[letter] = {pos for pos in values.matrix.pos(letter)}

    for mod in DIRECTIONS:
        for pos in positions[letters[0]]:
            pos_ = pos
            x_mas_position: tuple[int, int]
            for letter in letters[1:]:
                pos_ = tuple_add(pos_, mod)
                if letter == "A":
                    x_mas_position = pos_
                if pos_ not in positions[letter]:
                    break
            else:
                x_mas_positions.append(x_mas_position)

    for pos in set(x_mas_positions):
        if x_mas_positions.count(pos) > 1:
            result += 1

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  4
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day4/input
#
# Result: 1992
