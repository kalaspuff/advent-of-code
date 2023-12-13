from values import Values, values


def find_reflection_line(pattern: Values) -> set[int]:
    reflections = set()
    for i in range(len(pattern)):
        indices = pattern.indices(str(pattern[i]))
        if len(indices) <= 1:
            continue
        for rindex in indices[::-1]:
            if rindex > i and (rindex + i + 1) % 2 == 0 and (i == 0 or rindex == len(pattern) - 1):
                first = pattern[i : rindex + 1]
                last = pattern[rindex : (i - 1) if i else None : -1]
                if first.input == last.input:
                    reflections.add((rindex + i + 1) // 2)
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
