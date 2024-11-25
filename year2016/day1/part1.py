from values import values


async def run() -> int:
    result = [0, 0]

    current_direction = (0, 1)
    instructions = values.split(", ")
    for instruction in instructions:
        direction = instruction[0]
        distance = int(instruction[1:])

        if direction == "R":
            current_direction = (current_direction[1], -current_direction[0])
        else:
            current_direction = (-current_direction[1], current_direction[0])

        result[0] += current_direction[0] * distance
        result[1] += current_direction[1] * distance

    return abs(result[0]) + abs(result[1])


# [values.year]            (number)  2016
# [values.day]             (number)  1
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2016/day1/input
#
# Result: 239
