from helpers import paired, transform_tuple
from values import values


async def run() -> int:
    seed_values = transform_tuple(values.rows[0].split()[1:], (int, int, str))
    seed_ranges: set[tuple[int, int, int]] = {(*pair, 0) for pair in paired(seed_values)}

    maps: list[list[tuple[int, int, int]]] = []
    for row in values.rows[1:]:
        if row.endswith("map:"):
            maps.append([])
        elif row:
            map_entry: tuple[int, int, int] = transform_tuple(row.split(), (int, int, int))
            maps[-1].append(map_entry)

    for map_ in maps:
        updated_ranges = set()
        while seed_ranges:
            seed_range = seed_ranges.pop()
            if seed_range in updated_ranges:
                continue
            start, length, modifier = seed_range
            start += modifier
            end = start + length - 1
            for destination, source, sourcelen in map_:
                source_end = source + sourcelen - 1
                start_max = max(start, source)
                end_min = min(end, source_end)

                if source > end or source_end < start or min(end - start, source_end - source) < 0:
                    continue

                updated_ranges.add((start_max - modifier, end_min - start_max + 1, modifier + (destination - source)))

                if start < source:
                    seed_ranges.add((start - modifier, source - start, modifier))
                if end > source_end:
                    seed_ranges.add((source_end + 1 - modifier, end - source_end, modifier))

                break
            else:
                updated_ranges.add(seed_range)

        if updated_ranges:
            seed_ranges = updated_ranges.copy()
            updated_ranges = set()

    return min([start + modifier for start, length, modifier in seed_ranges])


# [values.year]            (number)  2023
# [values.day]             (number)  5
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day5/input
#
# Result: 125742456
