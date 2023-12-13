from values import values


def calculate_possibilities(
    possibilities: list[str],
    expected: tuple[str, ...],
    memo: dict[tuple[tuple[str, ...], tuple[str, ...]], int] | None = None,
) -> int:
    if memo is None:
        memo = {((), ()): 1, ((), ("",)): 1}

    key = (tuple(possibilities), expected)
    if key in memo:
        return memo[key]

    current, *rest = possibilities if possibilities else [""]

    match current:
        case ".":
            memo[key] = calculate_possibilities(rest, expected[1:] if not [*expected, ...][0] else expected, memo=memo)
        case "#" if not rest or not expected:
            memo[key] = 1 if expected == ("#",) else 0
        case "#" if rest[0] in (current_ := "#" if expected[0][1:] else ".", "?"):
            memo[key] = calculate_possibilities([current_, *rest[1:]], (expected[0][1:],) + expected[1:], memo=memo)
        case "?" if [*expected, ...][0]:
            memo[key] = sum(calculate_possibilities([char, *rest], expected, memo=memo) for char in ("#", "."))
        case "?":
            memo[key] = calculate_possibilities([".", *rest], expected, memo=memo)
        case _:
            memo[key] = 0

    return memo[key]


async def run() -> int:
    result = 0

    for folded_conditions, group_sizes_str in values.split_values():
        conditions = (folded_conditions * 5).join("?")
        group_sizes = group_sizes_str.ints() * 5
        expected = tuple("#" * size for size in group_sizes)
        result += calculate_possibilities(list(conditions), expected)
        continue

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  12
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day12/input
#
# Result: 37366887898686
