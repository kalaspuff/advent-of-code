# note: code may have been written in a rush, here be dragons and lots of bad patterns to avoid.

import functools
import itertools
import re
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    Union,
    cast,
    overload,
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


@functools.lru_cache(maxsize=128)
def binary_space_partitioning_lower_half(a: int, b: int) -> tuple[int, int]:
    return (a, int(a + (b + 1 - a) / 2 - 1))


@functools.lru_cache(maxsize=128)
def binary_space_partitioning_upper_half(a: int, b: int) -> tuple[int, int]:
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


def manhattan_distance(
    pos_1: Union[tuple[int, ...], tuple[int, int], map], pos_2: Union[tuple[int, ...], tuple[int, int], map]
) -> int:
    # also known as manhattan length, snake distance, taxicab metric, etc.
    pos_1 = tuple(pos_1) if isinstance(pos_1, map) else pos_1
    pos_2 = tuple(pos_1) if isinstance(pos_2, map) else pos_2
    return max(pos_1[0], pos_2[0]) - min(pos_1[0], pos_2[0]) + max(pos_1[1], pos_2[1]) - min(pos_1[1], pos_2[1])


def int_minus(value: Any, mod: Union[int, str] = 1) -> int:
    return int(value) - int(mod)


def int_plus(value: Any, mod: Union[int, str] = 1) -> int:
    return int(value) + int(mod)


def int_list(value: Sequence) -> List[int]:
    return list(map(int, value))


def int_rows(value: Sequence) -> List[int]:
    return int_list(value)


def tuple_sum(*values: tuple[int, ...]) -> tuple[int, ...]:
    result: List[int] = []

    for value in values:
        for i, v in enumerate(value):
            if len(result) <= i:
                result.append(0)
            result[i] += v

    return tuple(result)


def tuple_negative(value: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(-v for v in value)


def tuple_add(value: tuple[int, ...], mod: tuple[int, ...]) -> tuple[int, ...]:
    return tuple_sum(value, mod)


def tuple_sub(value: tuple[int, ...], mod: tuple[int, ...]) -> tuple[int, ...]:
    return tuple_sum(value, tuple_negative(mod))


def split_to_dict(
    values: Union[str, List[str]],
    split: Optional[Union[str, List[str], tuple[str, ...]]] = None,
    delimit: Optional[Union[str, List[str], tuple[str, ...]]] = None,
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
                result = {**result, **dict((cast(tuple[str, str], tuple(row.split(s, 1))),))}
                break

    return result


def match_rows(rows: List[str], regexp: str, transform: Optional[Union[tuple[Any, ...], List[Any]]] = None) -> Any:
    if not transform:
        transform = ()
    transform_all = str
    if not isinstance(transform, (tuple, list)):
        transform_all = transform
        transform = ()

    return [
        (
            transform_all(v) if len(transform) <= i else transform[i](v)
            for i, v in (
                enumerate(cast(re.Match[str], re.match(regexp, row)).groups())
                if re.match(regexp, row) is not None
                else ()
            )
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


def inverse_dict(
    value: Union[
        dict,
        tuple[tuple[Any, Any], ...],
        list[tuple[Any, Any]],
        list[list],
        Sequence[list],
        Sequence[tuple[Any, Any]],
        map,
    ],
    transform: Optional[Union[tuple, list[Any]]] = None,
) -> dict:
    if not transform:
        transform = ()

    if isinstance(value, map):
        value = cast(list[tuple[Any, Any]], list(value))

    if not isinstance(transform, (tuple, list)):
        transform = (transform, transform)

    return {
        (transform[0](k) if transform and transform[0] else k): (
            transform[1](v) if transform and len(transform) > 1 and transform[1] else v
        )
        for v, k in (value.items() if isinstance(value, dict) else value)
    }


def inverse_tuple(
    value: Union[tuple[Any, Any], list[Any], Sequence[Any], map], transform: Optional[Union[tuple, list[Any]]] = None
) -> tuple[Any, Any]:
    if not transform:
        transform = ()

    if isinstance(value, map):
        value = cast(tuple[Any, Any], tuple(value))

    if not isinstance(transform, (tuple, list)):
        transform = (transform, transform)

    return (transform[0](value[1]) if transform and transform[0] else value[1]), (
        transform[1](value[0]) if transform and len(transform) > 1 and transform[1] else value[0]
    )


def inverse_pairs(
    value: Union[
        list[tuple[Any, Any]],
        tuple[tuple[Any, Any], ...],
        tuple[list, ...],
        list[list],
        Sequence[list],
        Sequence[tuple[Any, Any]],
        map,
    ],
    transform: Optional[Union[tuple, list[Any]]] = None,
) -> Union[list[tuple[Any, Any]], list[list], tuple[tuple[Any, Any], ...], tuple[list, ...]]:
    if not transform:
        transform = ()

    if isinstance(value, map):
        value = cast(list[tuple[Any, Any]], list(value))

    if not isinstance(transform, (tuple, list)):
        transform = (transform, transform)

    return cast(Union[type[list], type[tuple]], type(value))(
        cast(Union[type[list], type[tuple]], type(v))(
            (
                (transform[0](v[1]) if transform and transform[0] else v[1]),
                (transform[1](v[0]) if transform and len(transform) > 1 and transform[1] else v[0]),
            )
        )
        for v in value
    )


def inverse_list(
    value: Union[
        list[tuple[Any, Any]],
        tuple[tuple[Any, Any], ...],
        list[list],
        Sequence[list],
        Sequence[tuple[Any, Any]],
        map,
    ],
    transform: Optional[Union[tuple, list[Any]]] = None,
) -> Union[list[tuple[Any, Any]], list[list]]:
    return cast(Union[list[tuple[Any, Any]], list[list]], list(inverse_pairs(value, transform=transform)))


def inverse(value: Any, transform: Optional[Union[tuple, list[Any]]] = None) -> Any:
    if not transform:
        transform = ()

    if isinstance(value, map):
        value = list(value)

    if isinstance(value, list) and value and isinstance(value[0], (tuple, list)) and len(value[0]) == 2:
        return inverse_pairs(value, transform=transform)
    if isinstance(value, tuple) and len(value) == 2:
        return inverse_tuple(cast(tuple[Any, Any], value), transform=transform)
    if isinstance(value, dict):
        return inverse_dict(value, transform=transform)
    raise NotImplementedError


def flip(value: Any, transform: Optional[Union[tuple, list[Any]]] = None) -> Any:
    return inverse(value, transform=transform)


def swap(value: Any, transform: Optional[Union[tuple, list[Any]]] = None) -> Any:
    return inverse(value, transform=transform)


def transform_dict(
    value: Union[
        dict,
        tuple[tuple[Any, Any], ...],
        list[tuple[Any, Any]],
        list[list],
        Sequence[list],
        Sequence[tuple[Any, Any]],
        map,
    ],
    transform: Optional[Union[tuple, list[Any]]] = None,
) -> dict:
    if not transform:
        transform = ()

    if isinstance(value, map):
        value = cast(list[tuple[Any, Any]], list(value))

    if not isinstance(transform, (tuple, list)):
        transform = (transform, transform)

    return {
        (transform[0](k) if transform and transform[0] else k): (
            transform[1](v) if transform and len(transform) > 1 and transform[1] else v
        )
        for k, v in (value.items() if isinstance(value, dict) else value)
    }


def transform_tuple(
    value: Union[
        list,
        tuple,
        map,
    ],
    transform: Optional[Union[tuple, list[Any]]] = None,
) -> tuple:
    if not transform:
        transform = ()

    if isinstance(value, map):
        value = tuple(value)

    if not isinstance(transform, (tuple, list)):
        transform = (transform,) * len(value)

    return tuple(
        transform[i](value[i]) if transform and len(transform) > i and transform[i] else value[i]
        for i in range(len(value))
    )


def transform_list(
    value: Union[
        list,
        tuple,
        map,
    ],
    transform: Optional[Union[tuple, list[Any]]] = None,
) -> list:
    if not transform:
        transform = ()

    if isinstance(value, map):
        value = list(value)

    if not isinstance(transform, (tuple, list)):
        transform = (transform,) * max(
            len(v) if isinstance(v, (tuple, list)) else (2 if isinstance(v, dict) else 1) for v in list(value)
        )

    return [
        (
            cast(Union[type[list], type[tuple]], type(v))(
                transform[i](v[i]) if transform and len(transform) > i and transform[i] else v[i] for i in range(len(v))
            )
        )
        if isinstance(v, (tuple, list))
        else transform_dict(v, transform=transform)
        if isinstance(v, dict)
        else (transform[0](v) if transform and transform[0] else v)
        for v in list(value)
    ]


def transform(value: Any, transform: Optional[Union[tuple[Any, ...], list[Any]]] = None) -> Any:
    if not transform:
        transform = ()

    if isinstance(value, map):
        value = list(value)

    if isinstance(value, list):
        return transform_list(value, transform=transform)
    if isinstance(value, tuple):
        return transform_tuple(value, transform=transform)
    if isinstance(value, dict):
        return transform_dict(value, transform=transform)
    raise NotImplementedError


def multisplit(
    value: str,
    separators: Union[
        str, list[Union[str, list[str], tuple[str]]], tuple[Union[str, list[str], tuple[str]], ...]
    ] = " ",
) -> list[Any]:
    result = [value]
    if isinstance(separators, str):
        separators = [separators]
    sep = separators[0]
    if not isinstance(sep, (list, tuple)):
        sep = (sep,)

    for sep_ in sep:
        sub_result: list[str] = []
        for r in result:
            sub_result += r.split(sep_)
        result = sub_result

    if len(separators) > 1:
        return [multisplit(r, separators[1:]) for r in result]

    return result


@overload
def batched(iterable: Iterable[T], n: Literal[1]) -> list[tuple[T]]:
    pass


@overload
def batched(iterable: Iterable[T], n: Literal[2]) -> list[tuple[T, T]]:
    pass


@overload
def batched(iterable: Iterable[T], n: Literal[3]) -> list[tuple[T, T, T]]:
    pass


@overload
def batched(iterable: Iterable[T], n: Literal[4]) -> list[tuple[T, T, T, T]]:
    pass


@overload
def batched(iterable: Iterable[T], n: Literal[5]) -> list[tuple[T, T, T, T, T]]:
    pass


@overload
def batched(iterable: Iterable[T], n: Literal[6]) -> list[tuple[T, T, T, T, T, T]]:
    pass


@overload
def batched(
    iterable: Iterable[T], n: int
) -> Union[
    list[tuple[T]],
    list[tuple[T, T]],
    list[tuple[T, T, T]],
    list[tuple[T, T, T, T]],
    list[tuple[T, T, T, T, T]],
    list[tuple[T, T, T, T, T, T]],
    list[tuple[T, ...]],
]:
    pass


def batched(
    iterable: Iterable[T], n: int
) -> Union[
    list[tuple[T]],
    list[tuple[T, T]],
    list[tuple[T, T, T]],
    list[tuple[T, T, T, T]],
    list[tuple[T, T, T, T, T]],
    list[tuple[T, T, T, T, T, T]],
    list[tuple[T, ...]],
]:
    if n < 1:
        raise ValueError("n must be at least one")

    result: list[tuple[T, ...]] = []
    while batch := tuple(itertools.islice(iter(iterable), n)):
        result.append(batch)

    return result


def paired(iterable: Iterable[T]) -> list[tuple[T, T]]:
    return batched(iterable, 2)


def pairwise(iterable: Iterable[T]) -> list[tuple[T, T]]:
    return list(itertools.pairwise(iterable))


def input_filepath():
    from values import values

    return values.input_filename


def input_basename():
    import os

    from values import values

    return values.input_filename.rpartition(os.sep)[-1]
