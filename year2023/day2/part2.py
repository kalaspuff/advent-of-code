from helpers import inverse_dict, multisplit
from values import values


async def run() -> int:
    result = 0

    for _, record in values.match_rows(r"^Game (\d+): (.*)$", transform=(int, str)):
        min_cubes = {"red": 0, "green": 0, "blue": 0}

        for rounds in multisplit(record, ["; ", ", "]):
            cubes = inverse_dict(map(str.split, rounds), transform=(str, int))
            min_cubes.update({color: max(min_cubes[color], count) for color, count in cubes.items()})

        result += min_cubes["red"] * min_cubes["green"] * min_cubes["blue"]

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  2
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day2/input
#
# Result: 78375
