from helpers import tuple_add, tuple_sub
from values import values


async def run() -> int:
    coordinates = set(values.matrix.coordinates)

    antennas_by_frequency: dict[str, set[tuple[int, int]]] = {}
    for pos, frequency in values.matrix.coordinates.items():
        if frequency.isalnum():
            antennas_by_frequency.setdefault(frequency, set()).add(pos)

    antinodes = set()

    for positions in antennas_by_frequency.values():
        for pos in positions:
            for pos_ in positions:
                if pos == pos_:
                    continue

                step = tuple_sub(pos, pos_)

                location_1 = pos
                location_2 = pos

                while location_1 in coordinates or location_2 in coordinates:
                    if location_1 in coordinates:
                        antinodes.add(location_1)
                    if location_2 in coordinates:
                        antinodes.add(location_2)

                    location_1 = tuple_add(location_1, step)
                    location_2 = tuple_sub(location_2, step)

    return len(antinodes)


# [values.year]            (number)  2024
# [values.day]             (number)  8
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day8/input
#
# Result: 1077
