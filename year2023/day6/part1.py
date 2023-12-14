from values import values


async def run() -> int:
    result = 1

    for time, record in zip(*values.ints()):
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
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day6/input
#
# Result: 588588
