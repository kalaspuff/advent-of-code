from helpers import inverse_dict, multisplit
from values import values


async def run() -> int:
    result = 0
    max_cubes = {"red": 12, "green": 13, "blue": 14}

    for game_id, record in values.match_rows(r"^Game (\d+): (.*)$", transform=(int, str)):
        for rounds in multisplit(record, ["; ", ", "]):
            cubes = inverse_dict(map(str.split, rounds), transform=(str, int))
            if any(cubes[color] > max_cubes[color] for color in cubes):
                break
        else:
            result += game_id

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  2
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day2/input
#
# Result: 2406
