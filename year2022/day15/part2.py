import itertools

from helpers import manhattan_distance, paired
from values import values


def calculate_exclusion_zone(sensor, distance, minmax):
    positions = set()
    sensor_x, sensor_y = sensor
    min_x, min_y, max_x, max_y = minmax

    for x in range(max(min_x, sensor_x - distance), min(max_x, sensor_x + distance + 1)):
        for range(max(min_y, sensor_y - distance), min(max_y, sensor_y + distance + 1)):
            if manhattan_distance(sensor, (x, y)) <= distance:
                positions.add((x, y))

    return positions


async def run():
    min_x = min_y = 0

    max_x = max_y = {"example": 20, "input": 4000000}[values.input_basename]
    multiplier = 4000000

    pairs = []
    positions = set()
    # positions = set(itertools.product(range(min_xy, max_xy + 1), range(min_xy, max_xy + 1)))

    for sensor, beacon in map(
        paired,
        values.match_rows(
            r"Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)", transform=(int, int, int, int)
        ),
    ):
        pairs.append((sensor, beacon))

    for sensor, beacon in pairs:
        if min_x <= sensor[0] <= max_x and min_x <= sensor[1] <= max_y:
            distance = manhattan_distance(sensor, beacon)
            positions |= calculate_exclusion_zone(sensor, distance)

    x, y = positions.pop()

    return x * multiplier + y


# [values.year]            (number)  2022
# [values.day]             (number)  15
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day15/input
#
# Result: ...
