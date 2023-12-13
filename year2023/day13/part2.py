from values import Values, values


def find_reflection_line(pattern: Values) -> set[int]:
    reflections = set()
    for n in (0, len(pattern) - 1):
        indices = [(n, i) if not n else (i, n) for i in pattern.indices(pattern[n]) if i != n and (i + n) % 2]
        for start, end in indices:
            sliced_pattern = pattern[start : end + 1]
            if sliced_pattern == sliced_pattern[::-1]:
                reflections.add((start + end + 1) // 2)
    return reflections


async def run() -> int:
    result = 0
    for pattern in values.split_sections("\n\n"):
        reflection: int | None = None
        old_horizontal = find_reflection_line(pattern)
        old_vertical = find_reflection_line(pattern.transpose()) if not old_horizontal else set()

        for y, row in enumerate(pattern):
            for x, c in enumerate(row):
                pattern_ = pattern.deepcopy()
                if c == "#":
                    pattern_[y][x] = "."
                elif c == ".":
                    pattern_[y][x] = "#"
                horizontal = find_reflection_line(pattern_) - old_horizontal
                vertical = find_reflection_line(pattern_.transpose()) - old_vertical
                if not horizontal and not vertical:
                    continue
                reflection = (horizontal.pop() * 100) if horizontal else (vertical.pop())
                result += reflection
                break
            if reflection is not None:
                break

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  13
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day13/input
#
# Result: 36755
