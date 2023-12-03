from helpers import manhattan_distance, paired
from values import values


def calculate_exclusion_zone(sensor, distance, target_y=None):
    positions = set()
    sensor_x, sensor_y = sensor

    if target_y is not None and manhattan_distance(sensor, (sensor[0], target_y)) > distance:
        return positions

    for x in range(sensor_x - distance, sensor_x + distance + 1):
        for y in [target_y] if target_y is not None else range(sensor_y - distance, sensor_y + distance + 1):
            if manhattan_distance(sensor, (x, y)) <= distance:
                positions.add((x, y))

    return positions


async def run():
    target_y = {"example": 10, "input": 2000000}[values.input_basename]

    pairs = []
    positions = set()
    beacons = set()

    for sensor, beacon in map(
        paired,
        values.match_rows(
            r"Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)", transform=(int, int, int, int)
        ),
    ):
        beacons.add(beacon)
        pairs.append((sensor, beacon))

    for sensor, beacon in pairs:
        distance = manhattan_distance(sensor, beacon)
        if manhattan_distance(sensor, (sensor[0], target_y)) <= distance:
            positions |= calculate_exclusion_zone(sensor, distance, target_y) - beacons

    return len(positions)


# [values.year]            (number)  2022
# [values.day]             (number)  15
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day15/input
#
# Result: 5166077
