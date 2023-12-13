from values import Values, values


def find_reflection_line(pattern: Values) -> int | None:
    for i in range(len(pattern)):
        indices = pattern.indices(pattern[i], i + 1)
        if not indices:
            continue
        for rindex in indices[::-1]:
            if (rindex + i + 1) % 2 == 0 and (i == 0 or rindex == len(pattern) - 1):
                first = pattern[i : rindex + 1]
                last = pattern[rindex : (i - 1) if i else None : -1]
                if first.input == last.input:
                    return (rindex + i + 1) // 2
    return None


async def run() -> int:
    result = 0

    for pattern in values.split_sections("\n\n"):
        horizontal = find_reflection_line(pattern)
        if horizontal is not None:
            result += horizontal * 100
            continue
        vertical = find_reflection_line(pattern.transpose())
        if vertical is not None:
            result += vertical

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  13
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day13/input
#
# Result: 35360
