import itertools
import sys

from matrix import Matrix
from values import values


class ContainedMatrix(Matrix):
    def as_str(self):
        result = ""
        for row in self.rows:
            result += f"{row[self.min_x:self.max_x]}\n"
        return result

    @property
    def min_x(self):
        return self._min_x

    @property
    def min_y(self):
        return self._min_y

    @property
    def max_x(self):
        return self._max_x


async def run():
    lowest_x = sys.maxsize
    highest_x = 0
    highest_y = 0

    for row in values.rows:
        points = [tuple(map(int, coords.split(","))) for coords in row.split(" -> ")]

        lowest_x = min(lowest_x, *map(lambda p: p[0], points))
        highest_x = max(highest_x, *map(lambda p: p[0], points))
        highest_y = max(highest_y, *map(lambda p: p[1], points))

    matrix = ContainedMatrix(None, width=highest_x * 2, height=highest_y + 3, fill=".")
    matrix._min_x = max(lowest_x - 1, 0) - 3
    matrix._max_x = max(highest_x + 1, 0) + 6

    for row in values.rows + [f"{matrix._min_x},{highest_y + 2} -> {matrix.width - 1},{highest_y + 2}"]:
        points = [tuple(map(int, coords.split(","))) for coords in row.split(" -> ")]

        for c1, c2 in itertools.pairwise(points):
            if c1[0] != c2[0]:
                for x in range(min(c1[0], c2[0]), max(c1[0], c2[0]) + 1):
                    matrix[x, c1[1]] = "#"
            else:
                for y in range(min(c1[1], c2[1]), max(c1[1], c2[1]) + 1):
                    matrix[c1[0], y] = "#"

    matrix[500, 0] = "+"
    sand_count = 0
    while True:
        sand = (500, 0)
        while True:
            if sand[1] >= highest_y + 1:
                matrix[sand] = "o"
                break

            if matrix[sand[0], sand[1] + 1] == ".":
                sand = (sand[0], sand[1] + 1)
                continue

            if matrix[sand[0] - 1, sand[1] + 1] == ".":
                sand = (sand[0] - 1, sand[1] + 1)
                continue

            if matrix[sand[0] + 1, sand[1] + 1] == ".":
                sand = (sand[0] + 1, sand[1] + 1)
                continue

            matrix[sand] = "o"

            if sand == (500, 0):
                print(matrix)
                return sand_count + 1

            break

        sand_count += 1


# [values.year]            (number)  2022
# [values.day]             (number)  14
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day14/input
#
# Result: 27566 low
