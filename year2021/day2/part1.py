from values import values


async def run():
    fwd = 0
    depth = 0
    for row in values.rows:
        cmd, num = row.split(" ")
        num = int(num)
        if cmd == "forward":
            fwd += num
        elif cmd == "down":
            depth += num
        elif cmd == "up":
            depth -= num
        else:
            raise Exception(f"Unknown command {cmd}")

    return fwd * depth


# [values.year]            (number)  2021
# [values.day]             (number)  2
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2021/day2/input
#
# Result: 1727835
