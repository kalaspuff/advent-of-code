from typing import cast

from matrix import Matrix
from values import values

XMAS_TREE = """
###############################
#.............................#
#.............................#
#.............................#
#.............................#
#..............#..............#
#.............###.............#
#............#####............#
#...........#######...........#
#..........#########..........#
#............#####............#
#...........#######...........#
#..........#########..........#
#.........###########.........#
#........#############........#
#..........#########..........#
#.........###########.........#
#........#############........#
#.......###############.......#
#......#################......#
#........#############........#
#.......###############.......#
#......#################......#
#.....###################.....#
#....#####################....#
#.............###.............#
#.............###.............#
#.............###.............#
#.............................#
#.............................#
#.............................#
#.............................#
###############################
""".strip()


async def run() -> int:
    width = 101
    height = 103

    robots = cast(list[tuple[int, int, int, int]], values.ints())

    second = 0
    while True:
        matrix = Matrix(width=width, height=height, fill=".")
        for x, y, *_ in robots:
            matrix[x, y] = "#"

        matrix_str = str(matrix)
        for row in XMAS_TREE.split("\n"):
            if row not in matrix_str:
                break
        else:
            return second

        robots_: list[tuple[int, int, int, int]] = []

        for x, y, velocity_x, velocity_y in robots:
            x_ = (x + velocity_x) % width
            y_ = (y + velocity_y) % height
            if x_ < 0:
                x_ = x_ + width
            if y_ < 0:
                y_ = y_ + height

            robots_.append((x_, y_, velocity_x, velocity_y))

        robots = robots_
        second += 1


# [values.year]            (number)  2024
# [values.day]             (number)  14
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day14/input
#
# Result: 8168
