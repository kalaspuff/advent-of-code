from values import values


async def run() -> int:
    result = 0
    time, record = values.replace(" ", "").flatten().ints()

    for hold_time in range(time):
        speed = hold_time
        travel_time = time - hold_time
        distance = speed * travel_time
        if distance > record:
            result += 1

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  6
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day6/input
#
# Result: 34655848
