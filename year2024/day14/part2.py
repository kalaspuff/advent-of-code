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

    robots = []
    for robot in values.ints():
        robots.append(robot)

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

        robots_ = []

        for x, y, velocity_x, velocity_y in robots:
            x += velocity_x
            y += velocity_y
            if x >= width:
                x = x - width
            if x < 0:
                x = x + width
            if y >= height:
                y = y - height
            if y < 0:
                y = y + height

            robots_.append((x, y, velocity_x, velocity_y))

        robots = robots_
        second += 1


# [values.year]            (number)  2024
# [values.day]             (number)  14
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day14/input
#
# Result: 8168
