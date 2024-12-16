from values import values


async def run() -> int:
    width = 101
    height = 103
    if values.input_basename == "example":
        width = 11
        height = 7

    robots = []
    for initial_x, initial_y, velocity_x, velocity_y in values.ints():
        x = initial_x
        y = initial_y

        for _ in range(100):
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

        robots.append((x, y))

    quadrants = [[] for _ in range(4)]
    for x, y in robots:
        if x == width // 2 or y == height // 2:
            continue

        if x >= 0 and x < width // 2 and y >= 0 and y < height // 2:
            quadrants[0].append((x, y))
        elif x >= width // 2 and y >= 0 and y < height // 2:
            quadrants[1].append((x, y))
        elif x >= 0 and x < width // 2 and y >= height // 2:
            quadrants[2].append((x, y))
        else:
            quadrants[3].append((x, y))

    result = 1
    for robots in quadrants:
        result *= len(robots)

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  14
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day14/input
#
# Result: 226236192
