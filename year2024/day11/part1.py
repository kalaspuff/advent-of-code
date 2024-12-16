from values import values


async def run() -> int:
    stones = list(values[0].ints())

    blinks = 25
    if values.input_basename == "example":
        blinks = 1

    for _ in range(blinks):
        stones_ = []
        for stone in stones:
            if stone == 0:
                stones_.append(1)
            elif len(str(stone)) % 2 == 0:
                stones_.append(int(str(stone)[: len(str(stone)) // 2]))
                stones_.append(int(str(stone)[len(str(stone)) // 2 :]))
            else:
                stones_.append(stone * 2024)

        stones = stones_

    return len(stones)


# [values.year]            (number)  2024
# [values.day]             (number)  11
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day11/input
#
# Result: 216996
