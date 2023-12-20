from helpers import Range, paired
from values import values


async def run() -> int:
    seed_ranges: set[tuple[Range, int]] = {
        (Range(start=start, stop=start + length), 0) for start, length in paired(values[0].ints())
    }
    maps = [rows.filter(lambda row: row.ints()).ints() for rows in values[1:].clean().split_sections("map:")[1:]]

    for map_ in maps:
        updated_ranges: set[tuple[Range, int]] = set()
        while seed_ranges:
            seed_range = seed_ranges.pop()
            updated_ranges.add(seed_range)

            range_, modifier = seed_range
            range_ = range_ + modifier

            for destination, source, sourcelen in map_:
                source_ = Range(start=source, stop=source + sourcelen)

                intersect_ = source_ & range_
                if not intersect_:
                    continue

                updated_ranges.remove(seed_range)
                updated_ranges.add((intersect_ - modifier, modifier + (destination - source)))

                if begin_range := range_.split(intersect_.start)[0]:
                    seed_ranges.add((begin_range - modifier, modifier))
                if end_range := range_.split(intersect_.stop)[1]:
                    seed_ranges.add((end_range - modifier, modifier))

                break

        if updated_ranges:
            seed_ranges = updated_ranges.copy()

    return min(min(range_ + modifier for range_, modifier in seed_ranges))


# [values.year]            (number)  2023
# [values.day]             (number)  5
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day5/input
#
# Result: 125742456
