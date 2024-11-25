from values import values


async def run() -> int:
    result = [0, 0]

    current_direction = (0, 1)
    instructions = values.split(", ")
    visited = set()
    for instruction in instructions:
        direction = instruction[0]
        distance = int(instruction[1:])

        if direction == "R":
            current_direction = (current_direction[1], -current_direction[0])
        else:
            current_direction = (-current_direction[1], current_direction[0])

        for _ in range(distance):
            result[0] += current_direction[0]
            result[1] += current_direction[1]

            if tuple(result) in visited:
                return abs(result[0]) + abs(result[1])

            visited.add(tuple(result))

    raise Exception("No intersection found")


# [values.year]            (number)  2016
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2016/day1/input
#
# Result: 141
