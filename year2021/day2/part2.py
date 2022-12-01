from values import values


async def run():
    fwd = 0
    depth = 0
    aim = 0
    for row in values.rows:
        cmd, num = row.split(" ")
        num = int(num)
        if cmd == "forward":
            fwd += num
            depth += aim * num
        elif cmd == "down":
            aim += num
        elif cmd == "up":
            aim -= num

    return fwd * depth


# [values.year]            (number)  2021
# [values.day]             (number)  2
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2021/day2/input
#
# Result: 1544000595
