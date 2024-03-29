from values import values


async def run() -> int:
    result = 0

    for _, *record in values.split_values([":", ";"]):
        min_cubes = {"red": 0, "green": 0, "blue": 0}
        for rounds in record:
            cubes = dict(zip(rounds.words(), rounds.ints()))
            min_cubes.update({color: max(min_cubes[color], count) for color, count in cubes.items()})
        result += min_cubes["red"] * min_cubes["green"] * min_cubes["blue"]

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  2
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day2/input
#
# Result: 78375
