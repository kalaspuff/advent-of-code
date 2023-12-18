from values import values


async def run() -> int | float:
    seeds: tuple[int, ...] = values[0].ints()
    maps = [rows.filter(lambda row: row.ints()).ints() for rows in values[1:].clean().split_sections("map:")]

    location = float("inf")
    for seed in seeds:
        number = seed
        for map_ in maps:
            for destination, source, sourcelen in map_:
                if number not in range(source, source + sourcelen):
                    continue
                number += destination - source
                break

        location = min(location, number)

    return location


# [values.year]            (number)  2023
# [values.day]             (number)  5
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day5/input
#
# Result: 196167384
