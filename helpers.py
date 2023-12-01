import functools
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union, cast


@functools.lru_cache(maxsize=128)
def binary_space_partitioning_lower_half(a: int, b: int) -> Tuple[int, int]:
    return (a, int(a + (b + 1 - a) / 2 - 1))


@functools.lru_cache(maxsize=128)
def binary_space_partitioning_upper_half(a: int, b: int) -> Tuple[int, int]:
    return (int(a + (b + 1 - a) / 2), b)


@functools.lru_cache(maxsize=128)
def binary_space_partitioning(
    value: Sequence, a: int, b: int, lower_modifier_char: Any, upper_modifier_char: Any
) -> int:
    for char in value:
        if char == lower_modifier_char:
            a, b = binary_space_partitioning_lower_half(a, b)
        if char == upper_modifier_char:
            a, b = binary_space_partitioning_upper_half(a, b)

    return b


def manhattan_distance(pos_1: Tuple[int, int], pos_2: Tuple[int, int]) -> int:
    # also known as manhattan length, snake distance, taxicab metric, etc.
    return max(pos_1[0], pos_2[0]) - min(pos_1[0], pos_2[0]) + max(pos_1[1], pos_2[1]) - min(pos_1[1], pos_2[1])


def int_minus(value: Any, mod: Union[int, str] = 1) -> int:
    return int(value) - int(mod)


def int_plus(value: Any, mod: Union[int, str] = 1) -> int:
    return int(value) + int(mod)


def int_list(value: Sequence) -> List[int]:
    return list(map(int, value))


def int_rows(value: Sequence) -> List[int]:
    return int_list(value)


def tuple_sum(*values: Tuple[int, ...]) -> Tuple[int, ...]:
    result: List[int] = []

    for value in values:
        for i, v in enumerate(value):
            if len(result) <= i:
                result.append(0)
            result[i] += v

    return tuple(result)


def tuple_negative(value: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple(-v for v in value)


def tuple_add(value: Tuple[int, ...], mod: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple_sum(value, mod)


def tuple_sub(value: Tuple[int, ...], mod: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple_sum(value, tuple_negative(mod))


def split_to_dict(
    values: Union[str, List[str]],
    split: Optional[Union[str, List[str], Tuple[str, ...]]] = None,
    delimit: Optional[Union[str, List[str], Tuple[str, ...]]] = None,
    strip: bool = True,
) -> Dict[str, str]:
    if isinstance(values, str):
        values = [values]

    if split is None:
        split = (",", " ", "\n")
    if isinstance(split, str):
        split = (split,)

    if delimit is None:
        delimit = (":", "=")
    if isinstance(delimit, str):
        delimit = (delimit,)

    merged_rows = []
    for row in values:
        split_rows = [row]
        for s in split:
            sub_result = []
            for r in split_rows:
                if strip:
                    r = r.strip()
                sub_result += r.split(s)
            split_rows = sub_result
        merged_rows += split_rows

    result: Dict[str, str] = {}
    for row in merged_rows:
        for s in delimit:
            if s in row:
                result = {**result, **dict((cast(Tuple[str, str], tuple(row.split(s, 1))),))}
                break

    return result


def match_rows(rows: List[str], regexp: str, transform: Optional[Union[Tuple[Any, ...], List[Any]]] = None) -> Any:
    if not transform:
        transform = ()
    transform_all = str
    if not isinstance(transform, (tuple, list)):
        transform_all = transform
        transform = ()

    return [
        (
            transform_all(v) if len(transform) <= i else transform[i](v)
            for i, v in enumerate(re.match(regexp, row).groups())
        )
        for row in rows
    ]  # type: ignore


def group_rows(rows: List[str], split: str = "", transform: Optional[Callable] = None) -> List[List[str]]:
    groups: List[List[str]] = []
    group: List[str] = []

    for row in rows:
        value = row
        if transform:
            value = transform(value)

        if value == split:
            groups.append(group)
            group = []
        else:
            group.append(row)

    if group:
        groups.append(group)

    return groups
