import itertools

from values import values


async def run() -> int:
    result = 0

    for conditions, group_sizes_str in values.split_values():
        group_sizes = group_sizes_str.ints()
        group_size_sum = sum(group_sizes)
        expected = tuple("#" * size for size in group_sizes)
        possibilities = tuple((".", "#") if v == "?" else (v,) for v in conditions)
        for conditions_ in itertools.product(*possibilities):
            if conditions_.count("#") != group_size_sum:
                continue
            current = tuple(v for v in "".join(conditions_).split(".") if v)
            if current == expected:
                result += 1

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  12
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day12/input
#
# Result: 7916
