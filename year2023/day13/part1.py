from values import Values, values


def find_reflection_line(pattern: Values) -> int:
    for n in (0, len(pattern) - 1):
        indices = [(n, i) if not n else (i, n) for i in pattern.indices(pattern[n]) if i != n and (i + n) % 2]
        for start, end in indices:
            sliced_pattern = pattern[start : end + 1]
            if sliced_pattern == sliced_pattern[::-1]:
                return (start + end + 1) // 2
    return 0


async def run() -> int:
    result = 0

    for pattern in values.split_sections("\n\n"):
        horizontal = find_reflection_line(pattern)
        result += horizontal * 100 if horizontal else find_reflection_line(pattern.transpose())

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  13
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day13/input
#
# Result: 35360
