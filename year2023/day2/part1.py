from values import values

MAX_CUBES = {"red": 12, "green": 13, "blue": 14}


async def run() -> int:
    result = 0

    for game_id, *record in values.split_values([":", ";"]):
        for rounds in record:
            cubes = {**MAX_CUBES, **dict(zip(rounds.words(), rounds.ints()))}
            if any(c > m for c, m in zip(cubes.values(), MAX_CUBES.values())):
                break
        else:
            result += game_id.ints()[0]

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  2
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day2/input
#
# Result: 2406
