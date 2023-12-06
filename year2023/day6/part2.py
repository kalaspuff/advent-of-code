from values import values


async def run() -> int:
    result = 1

    time = int("".join(values.rows[0].split()[1:]))
    record = int("".join(values.rows[1].split()[1:]))

    ways_to_win = 0
    for hold_time in range(time):
        speed = hold_time
        travel_time = time - hold_time
        distance = speed * travel_time
        if distance > record:
            ways_to_win += 1
    result *= ways_to_win

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  6
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day6/input
#
# Result: 34655848
