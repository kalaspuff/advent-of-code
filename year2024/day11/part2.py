from values import values

memo: dict[tuple[int, int], int] = {}


def stone_count(stone: int, steps: int) -> int:
    if steps == 0:
        return 1

    key = (stone, steps)
    if key in memo:
        return memo[key]

    if stone == 0:
        result = stone_count(1, steps - 1)
    elif len(str(stone)) % 2 == 0:
        left_part = stone_count(int(str(stone)[: len(str(stone)) // 2]), steps - 1)
        right_part = stone_count(int(str(stone)[len(str(stone)) // 2 :]), steps - 1)
        result = left_part + right_part
    else:
        result = stone_count(stone * 2024, steps - 1)

    memo[key] = result
    return result


async def run() -> int:
    stones = list(values[0].ints())

    return sum(stone_count(stone, 75) for stone in stones)


# [values.year]            (number)  2024
# [values.day]             (number)  11
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day11/input
#
# Result: 257335372288947
