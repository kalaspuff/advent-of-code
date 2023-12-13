from values import values


def calculate_possibilities(
    possibilities: tuple[tuple[str, ...], ...], expected: tuple[str, ...], memo: dict[tuple[tuple, ...], int]
) -> int:
    key = (possibilities, expected)
    if key in memo:
        return memo[key]

    if not possibilities:
        return 1 if (not expected or (not expected[0] and not expected[1:])) else 0

    current, *rest = possibilities
    count = 0
    if current == (".",):
        expected_ = expected[1:] if expected and not expected[0] else expected
        count += calculate_possibilities(tuple(rest), expected_, memo=memo)
    if current == ("#",) and expected and expected[0]:
        expected_ = (expected[0][1:],) + expected[1:]
        next_ = "#" if expected_[0] else "."
        if rest and len(rest[0]) > 1:
            count += calculate_possibilities(((next_,), *tuple(rest[1:])), expected_, memo=memo)
        elif (rest and rest[0] == (next_,)) or (not expected_[0] and not rest):
            count += calculate_possibilities(tuple(rest), expected_, memo=memo)
    if len(current) > 1:
        for current_ in current:
            if (not expected or not expected[0]) and current_ == "#":
                continue
            count += calculate_possibilities(((current_,), *tuple(rest)), expected, memo=memo)

    memo[key] = count
    return count


async def run() -> int:
    result = 0

    for folded_conditions, group_sizes_str in values.split_values():
        conditions = (folded_conditions * 5).join("?")
        group_sizes = group_sizes_str.ints() * 5
        expected = tuple("#" * size for size in group_sizes)
        possibilities = tuple((".", "#") if v == "?" else (v,) for v in conditions)
        result += calculate_possibilities(possibilities, expected, memo={})
        continue

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  12
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day12/input
#
# Result: 37366887898686
