from helpers import Range, paired
from values import values


async def run() -> int:
    seed_ranges: set[Range] = {Range(start=start, stop=start + length) for start, length in paired(values[0].ints())}
    maps = [rows.filter(lambda row: row.ints()).ints() for rows in values[1:].clean().split_sections("map:")[1:]]

    for map_ in maps:
        updated_ranges: set[Range] = set()
        while seed_ranges:
            range_ = seed_ranges.pop()

            for destination, source, sourcelen in map_:
                intersect_ = range_ & Range(start=source, stop=source + sourcelen)
                if not intersect_:
                    continue

                updated_ranges.add(intersect_ + destination - source)

                if begin_range := range_.split(intersect_.start)[0]:
                    seed_ranges.add(begin_range)
                if end_range := range_.split(intersect_.stop)[1]:
                    seed_ranges.add(end_range)

                break
            else:
                updated_ranges.add(range_)

        seed_ranges = updated_ranges.copy()

    return min(min(seed_ranges))


# [values.year]            (number)  2023
# [values.day]             (number)  5
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day5/input
#
# Result: 125742456
