# note: code may have been written in a rush, here be dragons and lots of bad patterns to avoid.
from __future__ import annotations

import functools
import itertools
import math
import re
from collections import Counter, deque
from itertools import combinations, permutations, product
from types import GenericAlias as _GenericAlias
from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    ParamSpec,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Union,
    Unpack,
    cast,
    overload,
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)

C = TypeVar("C", bound=Callable | tuple[Callable, ...])
C_co = TypeVar("C_co", bound=Callable, covariant=True)

R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)

P = ParamSpec("P")

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")

T1_co = TypeVar("T1_co", covariant=True)
T2_co = TypeVar("T2_co", covariant=True)
T3_co = TypeVar("T3_co", covariant=True)
T4_co = TypeVar("T4_co", covariant=True)
T5_co = TypeVar("T5_co", covariant=True)
T6_co = TypeVar("T6_co", covariant=True)

CT = Callable[..., T]

CTT1 = tuple[CT[T1]]
CTT2 = tuple[CT[T1], CT[T2]]
CTT3 = tuple[CT[T1], CT[T2], CT[T3]]
CTT4 = tuple[CT[T1], CT[T2], CT[T3], CT[T4]]
CTT5 = tuple[CT[T1], CT[T2], CT[T3], CT[T4], CT[T5]]
CTT6 = tuple[CT[T1], CT[T2], CT[T3], CT[T4], CT[T5], CT[T6]]

TTT1 = tuple[T1]
TTT2 = tuple[T1, T2]
TTT3 = tuple[T1, T2, T3]
TTT4 = tuple[T1, T2, T3, T4]
TTT5 = tuple[T1, T2, T3, T4, T5]
TTT6 = tuple[T1, T2, T3, T4, T5, T6]

CTTT1 = CTT1[T]
TTTT1 = TTT1[T]
CTTT2 = CTT2[T, T]
TTTT2 = TTT2[T, T]
CTTT3 = CTT3[T, T, T]
TTTT3 = TTT3[T, T, T]


@overload
def type_from_tuple(
    val: tuple[
        Callable[..., T1], Callable[..., T2], Callable[..., T3], Callable[..., T4], Callable[..., T5], Callable[..., T6]
    ],
) -> tuple[T1, T2, T3, T4, T5, T6]:
    return cast(tuple[T1, T2, T3, T4, T5, T6], ...)


@overload
def type_from_tuple(
    val: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3], Callable[..., T4], Callable[..., T5]],
) -> tuple[T1, T2, T3, T4, T5]:
    return cast(tuple[T1, T2, T3, T4, T5], ...)


@overload
def type_from_tuple(
    val: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3], Callable[..., T4]],
) -> tuple[T1, T2, T3, T4]:
    return cast(tuple[T1, T2, T3, T4], ...)


@overload
def type_from_tuple(val: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3]]) -> tuple[T1, T2, T3]:
    return cast(tuple[T1, T2, T3], ...)


@overload
def type_from_tuple(val: tuple[Callable[..., T1], Callable[..., T2]]) -> tuple[T1, T2]:
    return cast(tuple[T1, T2], ...)


@overload
def type_from_tuple(val: tuple[Callable[..., T1]]) -> tuple[T1]:
    return cast(tuple[T1], ...)


@overload
def type_from_tuple(val: tuple[Callable[..., T], ...]) -> tuple[T, ...]:
    return cast(tuple[T, ...], ...)


def type_from_tuple(val: Any) -> tuple[Any, ...]:
    return cast(tuple[Any, ...], ...)


class ReturnTypeMeta(Protocol[C_co]):
    def __class_getitem__(cls, item: Callable[P, R]) -> type["ReturnType[P, R]"]:
        def get_types(item: Callable[P, R]) -> R:
            return cast(R, ...)

        args: tuple[R] = (get_types(item),)
        result = type(
            f"ReturnType{item}",
            (cls,),
            {
                "__args__": args,
                "__parameters__": item,
                "__qualname__": f"ReturnType[{args[0]}]",
                "__module__": "helpers",
                "__repr__": lambda self: f"ReturnType[{args[0]}]",
                "__func__": item,
                "__orig_class__": cls,
            },
        )
        return cast(type["ReturnType[P, R]"], result)


class ReturnType(ReturnTypeMeta[Callable[P, R]], _GenericAlias):
    __args__: tuple[P, R]
    __return_class__: R

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.__orig_class__.__args__[0](*args, **kwargs)


_ReturnType = ReturnType
ReturnTypeT = Callable[..., T]


def testfunc(arg: ReturnTypeT[T]) -> T:
    return arg(1, 2)


class IteratorExhaustedError(Exception):
    result: list[Any]


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
    pos_1: Union[tuple[int, ...], tuple[int, int], map, range],
    pos_2: Union[tuple[int, ...], tuple[int, int], map, range],
) -> int:
    # also known as manhattan length, snake distance, taxicab metric, etc.
    if isinstance(pos_1, range) and isinstance(pos_2, range):
        return len(range(pos_1.start, pos_1.stop - 1, pos_1.step)) + len(range(pos_2.start, pos_2.stop - 1, pos_2.step))
    pos_1 = tuple(pos_1) if isinstance(pos_1, map) else pos_1
    pos_2 = tuple(pos_1) if isinstance(pos_2, map) else pos_2
    return max(pos_1[0], pos_2[0]) - min(pos_1[0], pos_2[0]) + max(pos_1[1], pos_2[1]) - min(pos_1[1], pos_2[1])


def position_ranges(
    pos_1: Union[tuple[int, ...], tuple[int, int], map], pos_2: Union[tuple[int, ...], tuple[int, int], map]
) -> tuple[range, range]:
    pos_1 = tuple(pos_1) if isinstance(pos_1, map) else pos_1
    pos_2 = tuple(pos_1) if isinstance(pos_2, map) else pos_2
    return range(min(pos_1[0], pos_2[0]), max(pos_1[0], pos_2[0]) + 1), range(
        min(pos_1[1], pos_2[1]), max(pos_1[1], pos_2[1]) + 1
    )


def int_minus(value: Any, mod: Union[int, str] = 1) -> int:
    return int(value) - int(mod)


def int_plus(value: Any, mod: Union[int, str] = 1) -> int:
    return int(value) + int(mod)


def int_list(value: Sequence) -> list[int]:
    return list(map(int, value))


def int_rows(value: Sequence) -> list[int]:
    return int_list(value)


@overload
def tuple_sum(*values: tuple[int, int]) -> tuple[int, int]:
    ...


@overload
def tuple_sum(*values: tuple[int, ...]) -> tuple[int, ...]:
    ...


@overload
def tuple_sum(*values: T) -> T:
    ...


def tuple_sum(*values: T) -> T:
    result: list[int] = []

    for value in values:
        for i, v in enumerate(cast(Iterable, value)):
            if len(result) <= i:
                result.append(0)
            result[i] += v

    return cast(T, tuple(result))


@overload
def tuple_negative(value: tuple[int, int]) -> tuple[int, int]:
    ...


@overload
def tuple_negative(value: tuple[int, ...]) -> tuple[int, ...]:
    ...


@overload
def tuple_negative(value: T) -> T:
    ...


def tuple_negative(value: T) -> T:
    return cast(T, tuple(-v for v in cast(Iterable, value)))


@overload
def tuple_add(value: tuple[int, int], mod: tuple[int, int]) -> tuple[int, int]:
    ...


@overload
def tuple_add(value: tuple[int, ...], mod: tuple[int, ...]) -> tuple[int, ...]:
    ...


@overload
def tuple_add(value: T, mod: T) -> T:
    ...


def tuple_add(value: T, mod: T) -> T:
    return cast(T, tuple_sum(value, mod))


@overload
def tuple_sub(value: tuple[int, int], mod: tuple[int, int]) -> tuple[int, int]:
    ...


@overload
def tuple_sub(value: tuple[int, ...], mod: tuple[int, ...]) -> tuple[int, ...]:
    ...


@overload
def tuple_sub(value: T, mod: T) -> T:
    ...


def tuple_sub(value: T, mod: T) -> T:
    return tuple_sum(value, tuple_negative(mod))


def split_to_dict(
    values: Union[str, list[str]],
    split: Optional[Union[str, list[str], tuple[str, ...]]] = None,
    delimit: Optional[Union[str, list[str], tuple[str, ...]]] = None,
    strip: bool = True,
) -> dict[str, str]:
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
                sub_result += r.strip().split(s) if strip else r.split(s)
            split_rows = sub_result
        merged_rows += split_rows

    result: dict[str, str] = {}
    for row in merged_rows:
        for s in delimit:
            if s in row:
                result = {**result, **dict((cast(tuple[str, str], tuple(row.split(s, 1))),))}
                break

    return result


def match_rows(
    rows: list[str], regexp: str, transform: Optional[Union[tuple[Any, ...], list[Any], Callable[..., Any]]] = None
) -> Any:
    if not transform:
        transform = ()
    transform_all: Callable[..., Any] = str
    if not isinstance(transform, (tuple, list)):
        transform_all = transform
        transform = ()

    return [
        tuple(
            transform_all(v) if len(transform) <= i else transform[i](v)
            for i, v in (
                enumerate(cast(re.Match[str], re.match(regexp, row)).groups())
                if re.match(regexp, row) is not None
                else ()
            )
        )
        for row in rows
    ]


def findall_rows(
    rows: list[str], regexp: str, transform: Optional[Union[tuple[Any, ...], list[Any], Callable[..., Any]]] = None
) -> Any:
    if not transform:
        transform = ()
    transform_all: Callable[..., Any] = str
    if not isinstance(transform, (tuple, list)):
        transform_all = transform
        transform = ()

    return [
        tuple(
            transform_all(v) if len(transform) <= i else transform[i](v)
            for i, v in (enumerate(re.findall(regexp, row)) if re.findall(regexp, row) is not None else ())
        )
        for row in rows
    ]


def group_rows(rows: list[str], split: str = "", transform: Optional[Callable] = None) -> list[list[str]]:
    groups: list[list[str]] = []
    group: list[str] = []

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
    transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None,
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
    value: Union[tuple[Any, Any], list[Any], Sequence[Any], map],
    transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None,
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
    transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None,
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
    transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None,
) -> Union[list[tuple[Any, Any]], list[list]]:
    return cast(Union[list[tuple[Any, Any]], list[list]], list(inverse_pairs(value, transform=transform)))


def inverse(value: Any, transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None) -> Any:
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


def flip(value: Any, transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None) -> Any:
    return inverse(value, transform=transform)


def swap(value: Any, transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None) -> Any:
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
    transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None,
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


@overload
def transform_tuple(
    value,
    transform: Callable[..., T],
) -> tuple[T, ...]:
    ...


@overload
def transform_tuple(
    value,
    transform: tuple[Callable[..., T1]],
) -> tuple[T1]:
    ...


@overload
def transform_tuple(
    value,
    transform: tuple[Callable[..., T1], Callable[..., T2]],
) -> tuple[T1, T2]:
    ...


@overload
def transform_tuple(
    value,
    transform: tuple[Callable[..., T], ...],
) -> tuple[T, ...]:
    ...


@overload
def transform_tuple(
    value: Union[
        list,
        tuple,
        deque,
        map,
    ],
    transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None,
) -> tuple:
    ...


def transform_tuple(
    value: Union[
        list,
        tuple,
        deque,
        map,
    ],
    transform: Optional[
        Union[
            Callable[..., Any],
            tuple[Callable[..., Any], ...],
            tuple[Callable[..., Any]],
            tuple[Callable[..., Any], Callable[..., Any]],
            list[Any],
            Callable[..., Any],
        ]
    ] = None,
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


def transform_deque(
    value: Union[
        list,
        tuple,
        deque,
        map,
    ],
    transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None,
) -> deque:
    result = transform_list(value, transform=transform)
    if isinstance(value, deque) and value.maxlen:
        return deque(result, maxlen=value.maxlen)
    return deque(result)


def transform_list(
    value: Union[
        list,
        tuple,
        deque,
        map,
    ],
    transform: Optional[Union[tuple, list[Any], Callable[..., Any]]] = None,
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


def transform(value: Any, transform: Optional[Union[tuple[Any, ...], list[Any], Callable[..., Any]]] = None) -> Any:
    if not transform:
        transform = ()

    if isinstance(value, map):
        value = list(value)

    if isinstance(value, list):
        return transform_list(value, transform=transform)
    if isinstance(value, tuple):
        return transform_tuple(value, transform=transform)
    if isinstance(value, deque):
        return transform_deque(value, transform=transform)
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
    iter_ = iter(iterable)

    try:
        while (part_ := next(iter_)) or True:
            try:
                batch = (part_, *tuple(next(iter_) for _ in range(n - 1)))
            except RuntimeError as exc:
                length = 0
                try:
                    for _ in iter(iterable):
                        length += 1
                except RuntimeError:
                    pass
                batch_number = len(result) + 1
                missing_items = length - n * (batch_number - 1)
                exception = IteratorExhaustedError(
                    f"batched() iterator was prematurely exhausted (length={length}, n={n}, "
                    + f"batch_number={len(result) + 1}, missing_items={missing_items})"
                )
                exception.result = result
                raise exception from exc

            result.append(batch)
    except StopIteration as exc:
        if not result:
            exception = IteratorExhaustedError("batched() was called on an iterator that was already exhausted")
            exception.result = result
            raise exception from exc
        return result

    return result


@overload
def paired(iterable: tuple[T1, T2]) -> list[tuple[T1, T2]]:
    ...


@overload
def paired(iterable: tuple[T1, T2, T1, T2]) -> list[tuple[T1, T2]]:
    ...


@overload
def paired(iterable: tuple[T1, T2, T1, T2, T1, T2]) -> list[tuple[T1, T2]]:
    ...


@overload
def paired(iterable: Iterable[T] | tuple[T, ...]) -> list[tuple[T, T]]:
    ...


def paired(iterable: Iterable[Any] | tuple[Any, ...]) -> list[tuple[Any, Any]]:
    return batched(iterable, 2)


def pairwise(iterable: Iterable[T]) -> list[tuple[T, T]]:
    return list(itertools.pairwise(iterable))


class Range:
    def __init__(
        self,
        /,
        value: int | range | slice | Range | None = None,
        stop_: int | None = None,
        step_: int | None = None,
        *,
        start: int | None = None,
        stop: int | None = None,
        end: int | None = None,
        step: int | None = None,
    ) -> None:
        if stop is not None and not isinstance(stop, int):
            raise TypeError(f"stop ({stop}) must be int")
        if start is not None and not isinstance(start, int):
            raise TypeError(f"start ({start}) must be int")
        if end is not None and not isinstance(end, int):
            raise TypeError(f"end ({end}) must be int")
        if step is not None and not isinstance(step, int):
            raise TypeError(f"step ({step}) must be int")

        if value is not None and not isinstance(value, (int, range, slice, Range)):
            raise TypeError(f"first unnamed argument ({value}) must be int, range, slice or Range if specified")
        if stop_ is not None and (not isinstance(value, int) or not isinstance(stop_, int)):
            raise TypeError("all unnamed arguments must be int if more than one argument is specified")
        if step_ is not None and (
            not isinstance(value, int) or not isinstance(stop_, int) or not isinstance(step_, int)
        ):
            raise TypeError("all unnamed arguments must be int if more than one argument is specified")

        if stop_ is not None:
            stop = stop if stop is not None else stop_
            if stop != stop_:
                raise ValueError(f"cannot specify different stop values ({stop} != {stop_})")
        if step_ is not None:
            step = step if step is not None else step_
            if step != step_:
                raise ValueError(f"cannot specify different step values ({step} != {step_})")

        if value is not None and isinstance(value, int) and stop is None and end is None:
            start = start if start is not None else 0
            stop = value
        elif value is not None and isinstance(value, int) and start is None and (stop is not None or end is not None):
            start = value
        elif value is not None and isinstance(value, (range, slice, Range)):
            start = start if start is not None else (value.start if isinstance(value.start, int) else 0)
            if not isinstance(value.stop, int):
                raise TypeError(f"value.stop ({value.stop}) must be int, unbound slice not supported")
            stop = (
                stop
                if stop is not None
                else (end + 1 if end is not None else (value.stop if isinstance(value.stop, int) else 0))
            )
            step = step if step is not None else (value.step if isinstance(value.step, int) else 1)
        elif value is not None:
            raise TypeError(f"value ({value}) must be int, range or slice")

        if stop is not None and end is not None and stop - 1 != end:
            raise ValueError(f"stop ({stop}) - 1 != end ({end})")
        if step is not None and not step:
            raise ValueError(f"step ({step}) must not be zero")

        if end is None and stop is not None:
            end = stop - 1
        elif end is not None and stop is None:
            stop = end + 1

        if end is None or stop is None:
            raise ValueError("must specify either end or stop")

        start = start or 0

        self.start: int = start
        self.end: int = end
        self.stop: int = stop
        self.step: int = 1 if step is None else step
        self._range: range = range(self.start, self.stop, self.step)
        self._slice: slice = slice(self.start, self.stop, self.step)

    def index(self, value: int) -> int:
        return self._range.index(value)

    def index_near(self, value: int) -> int:
        if value < self.start:
            return 0
        if value > self.end:
            return len(self) - 1
        for value_ in range(value, self.stop, 1):
            if self.count(value_):
                return self._range.index(value_)
        raise ValueError(f"value ({value}) not in range")

    def count(self, value: int) -> int:
        return self._range.count(value)

    def __repr__(self) -> str:
        if len(self) == 0:
            return f"EmptyRange(length={len(self)})"
        if self.step == 1:
            return f"Range(start={self.start}, end={self.end}, _range={self._range}, length={len(self)})"
        return f"Range(start={self.start}, end={self.end}, step={self.step}, _range={self._range}, length={len(self)})"

    def __len__(self) -> int:
        return max(0, (self.end - self.start) // self.step + 1)

    def __iter__(self) -> Iterator[int]:
        return iter(self._range)

    def __contains__(self, value: int) -> bool:
        return bool(self.count(value))

    @overload
    def __getitem__(self, idx: int) -> int:
        ...

    @overload
    def __getitem__(self, idx: slice) -> Range:
        ...

    def __getitem__(self, idx: int | slice) -> int | Range:
        if isinstance(idx, int):
            return self._range[idx]
        _range = self._range[idx]
        if idx.stop is None or idx.stop >= len(self._range):
            return Range(_range, stop=self._range.stop)
        return Range(self._range[idx])

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, (Range, range, slice)):
            return False
        other_ = Range(int(other), int(other) + 1) if isinstance(other, int) else Range(other)
        if (
            self.start == other_.start
            and self.stop == other_.stop
            and self.end == other_.end
            and self.step == other_.step
        ):
            return True
        return False

    def __gt__(self, other: int) -> bool:
        return other < self.start

    def __ge__(self, other: int) -> bool:
        return other <= self.end

    def __lt__(self, other: int) -> bool:
        return other > self.end

    def __le__(self, other: int) -> bool:
        return other >= self.start

    def __hash__(self) -> int:
        return hash(("Range", self.start, self.stop, self.end, self.step))

    def __copy__(self) -> Range:
        return Range(self)

    def copy(self) -> Range:
        return self.__copy__()

    def __deepcopy__(self, memo: dict | None) -> Range:
        return Range(self)

    def deepcopy(self) -> Range:
        return self.__deepcopy__(None)

    def __reduce__(self) -> tuple[type[Range], tuple[int, int, int, int]]:
        return (Range, (self.start, self.stop, self.end, self.step))

    def __add__(self, other: int) -> Range:
        return Range(start=self.start + other, end=self.end + other, step=self.step)

    def __radd__(self, other: int) -> Range:
        return Range(start=self.start + other, end=self.end + other, step=self.step)

    def __sub__(self, other: int) -> Range:
        return self.__add__(-other)

    def __rsub__(self, other: int) -> Range:
        return self.__radd__(-other)

    def __iadd__(self, other: int) -> None:
        self.start += other
        self.stop += other
        self.end += other
        self._range = range(self.start, self.stop, self.step)
        self._slice = slice(self.start, self.stop, self.step)

    def __isub__(self, other: int) -> None:
        self.__iadd__(-other)

    def __and__(self, other: int | range | slice | Range) -> Range:
        if isinstance(other, slice):
            other = slice(other.start or self.start, other.stop or self.stop, other.step or self.step)
        other_ = Range(int(other), int(other) + 1) if isinstance(other, int) else Range(other)
        # if other_.step != self.step and max(other_.step, self.step) % min(other_.step, self.step) != 0:
        #    raise ValueError(f"step ({self.step}) must be evenly divisible with other step ({other_.step})")

        start = max(self.start, other_.start)
        end = min(self.end, other_.end)
        step = math.lcm(other_.step, self.step)

        for _ in range(step):
            if start in self and start in other_:
                break
            start += 1
        else:
            return EmptyRange()

        result = Range(
            start=start,
            end=end,
            step=step,
        )
        return result or EmptyRange()

    def __rand__(self, other: int | range | slice | Range) -> Range:
        return self.__and__(other)

    def __or__(self, other: int | range | slice | Range) -> Range | Ranges:
        other_ = Range(int(other), int(other) + 1) if isinstance(other, int) else Range(other)
        if not self or not other_:
            return self or other_ or EmptyRange()

        if (
            (other_.step != self.step and max(other_.step, self.step) % min(other_.step, self.step) != 0)
            or (other_.step != self.step and (self.start != other_.start or self.end != other_.end))
            or (other_.start > self.stop or other_.stop < self.start)
            or not self.__and__(other_)
        ):
            if other_.step == self.step and (
                other_[0] - other_.step == self[-1] or other_[-1] + other_.step == self[0]
            ):
                # edge case: adjacent non-intersect
                return Range(
                    start=min(self.start, other_.start),
                    end=max(self.end, other_.end),
                    step=min(other_.step, self.step),
                )

            result_ = Ranges(self, other_)
            if not result_:
                return EmptyRange()
            if len(result_.ranges) == 1:
                return result_.ranges[0]
            return result_

        return Range(
            start=min(self.start, other_.start),
            end=max(self.end, other_.end),
            step=min(other_.step, self.step),
        )

    def __ror__(self, other: int | range | slice | Range) -> Range | Ranges:
        return self.__or__(other)

    def __bool__(self) -> bool:
        return bool(len(self))

    def __cmp__(self, other: int | range | slice | Range) -> int:
        other_ = Range(int(other), int(other) + 1) if isinstance(other, int) else Range(other)
        self_cmp = (self.start, self.stop, self.end, self.step, str(type(self)))
        other_cmp = (other_.start, other_.stop, other_.end, other_.step, str(type(other)))
        if self_cmp > other_cmp:
            return 1
        if self_cmp < other_cmp:
            return -1
        return 0

    @property
    def _sort_value(self) -> tuple[int, int, int, int, str]:
        return (self.start, self.stop, self.end, self.step, str(type(self)))

    def __int__(self) -> int:
        if len(self) != 1:
            raise ValueError(f"cannot convert range with length {len(self)} to int")
        return self.start

    def split(self, value: int) -> tuple[Range, Range]:
        idx = self.index_near(value)
        return self[:idx], self[idx:]


class EmptyRange(Range):
    def __init__(self) -> None:
        super().__init__(0)


class Ranges:
    ranges: list[Range]
    _reentrancy_guard: bool = False

    def __init__(self, *ranges: int | range | slice | Range | Ranges) -> None:
        result: list[Range] = []
        for r in ranges:
            if isinstance(r, Ranges):
                result.extend(r.ranges)
            elif isinstance(r, int):
                result.append(Range(int(r), int(r) + 1))
            else:
                result.append(Range(r))

        if type(self)._reentrancy_guard:
            self.ranges = sorted(result, key=lambda r: r._sort_value)
            return

        # examples:
        # (Range(10, 28, 3) | Range(3, 25, 1))
        # (Range(10, 28, 3) | Range(3, 25, 2))
        # Range(1, 5).__or__(Range(0, 6, 2))
        # Range(0, 6, 2).__or__(Range(1, 5))
        # Range(1, 5).__or__(Range(5, 6))
        # Range(1, 5).__or__(Range(0, 10, 2))
        # [i for i in (Range(10, 28, 3) | Range(2, 25, 2))]

        while True:
            current = result[:]
            result_ = []
            while result:
                range_ = result.pop(0)
                if not range_:
                    continue
                if range_ in result:
                    continue
                for r_ in result:
                    intersection = r_ & range_
                    if intersection and intersection not in (r_, range_):
                        if max(r_.step, range_.step) % min(r_.step, range_.step) == 0:
                            combined_ranges = []
                            mid_intersection: Range
                            if range_[0] < r_[0]:
                                mid_intersection = Range(
                                    start=min(intersection[0], r_[0]),
                                    end=intersection.end,
                                    step=min(r_.step, range_.step),
                                )
                            else:
                                mid_intersection = Range(
                                    start=min(intersection[0], range_[0]),
                                    end=intersection.end,
                                    step=min(r_.step, range_.step),
                                )
                            if mid_intersection:
                                combined_ranges.append(mid_intersection)

                            before_intersection: Range
                            if range_[0] < r_[0]:
                                before_intersection = Range(
                                    start=min(range_[0], mid_intersection[0]),
                                    stop=mid_intersection[0],
                                    step=range_.step,
                                )
                            else:
                                before_intersection = Range(
                                    start=min(r_[0], mid_intersection[0]),
                                    stop=mid_intersection[0],
                                    step=r_.step,
                                )
                            if before_intersection:
                                combined_ranges.append(before_intersection)

                            after_intersection: Range
                            if range_[-1] > r_[-1]:
                                after_intersection = Range(
                                    start=intersection.end + mid_intersection.step,
                                    end=range_[-1],
                                    step=range_.step,
                                )
                                if after_intersection:
                                    for _ in range(range_.step):
                                        if after_intersection[0] in range_:
                                            break
                                        after_intersection = Range(
                                            after_intersection, start=after_intersection.start + 1
                                        )
                            else:
                                after_intersection = Range(
                                    start=intersection.end + mid_intersection.step,
                                    end=r_[-1],
                                    step=r_.step,
                                )
                                if after_intersection:
                                    for _ in range(range_.step):
                                        if after_intersection[0] in r_:
                                            break
                                        after_intersection = Range(
                                            after_intersection, start=after_intersection.start + 1
                                        )
                            if after_intersection:
                                combined_ranges.append(after_intersection)

                            while r_ in result:
                                result.remove(r_)
                            result.extend(combined_ranges)
                            break

                        # todo: ranges with different step-sizes that aren't evenly divisible
                        # [i for i in (Range(10, 28, 3) | Range(2, 25, 2))]
                        raise NotImplementedError("non-evenly divisible step not implemented")

                    type(self)._reentrancy_guard = True
                    try:
                        # todo: ranges with same step size, but different offset
                        # [i for i in (Range(10, 28, 3) | Range(2, 25, 3))]
                        unified_range = r_ | range_
                        type(self)._reentrancy_guard = False
                        if (
                            not unified_range
                            or len(unified_range) == len(range_)
                            or len(unified_range) == len(r_)
                            or len(unified_range) == len(r_) + len(range_)
                        ):
                            continue
                        if isinstance(unified_range, Ranges):
                            result.extend(unified_range.ranges)
                            break
                        if isinstance(unified_range, Range):
                            result.append(unified_range)
                            break
                    finally:
                        type(self)._reentrancy_guard = False
                else:
                    result_.append(range_)
            result = sorted(result_, key=lambda r: r._sort_value)
            if result == current:
                break

        self.ranges = result

    def index(self, value: int) -> int:
        idx = 0
        for r in self.ranges:
            if r.count(value):
                return idx + r.index(value)
            idx += len(r)
        raise ValueError(f"value ({value}) not in range")

    def index_near(self, value: int) -> int:
        idx = 0
        start = end = self[0]
        if value < start:
            return 0
        for r in self.ranges:
            end = r[-1]
            if value >= start and value <= end:
                return idx + r.index_near(value)
            idx += len(r)
        if value > end:
            return idx
        raise ValueError(f"value ({value}) not in range")

    def count(self, value: int) -> int:
        result = 0
        for r in self.ranges:
            result += r.count(value)
        return result

    def __repr__(self) -> str:
        return f"Ranges({self.ranges})"

    def __len__(self) -> int:
        return sum(len(r) for r in self.ranges)

    def __iter__(self) -> Iterator[int]:
        for r in self.ranges:
            yield from r

    def __contains__(self, value: int) -> bool:
        return any(value in r for r in self.ranges)

    @overload
    def __getitem__(self, idx: int) -> int:
        ...

    @overload
    def __getitem__(self, idx: slice) -> Ranges | Range:
        ...

    def __getitem__(self, idx: int | slice) -> int | Ranges | Range:
        if isinstance(idx, int):
            idx_ = idx
            if idx_ < 0:
                idx_ = len(self) + idx_
            for r in self.ranges:
                if idx_ < len(r):
                    return r[idx_]
                idx_ -= len(r)
            raise IndexError(f"index ({idx}) out of range")
        result = []
        start = idx.start if idx.start is not None else 0
        stop = idx.stop if idx.stop is not None else len(self)
        step = idx.step if idx.step is not None else 1
        if start < 0:
            start = len(self) + start
        if stop < 0:
            stop = len(self) + stop
        carry = 0
        for r in self.ranges:
            if start < 0:
                start = carry
            range_ = r[start:stop:step]
            result.append(range_)
            start -= len(r)
            stop -= len(r)
            carry = len(r[start::step]) * step - len(r[start:])
            if stop <= 0:
                break
        return Ranges(*result)

    def __bool__(self) -> bool:
        return bool(len(self))

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if isinstance(other, (int, range, slice, Range)):
            other = Ranges(Range(int(other), int(other) + 1) if isinstance(other, int) else Range(other))
        if not isinstance(other, Ranges):
            return False
        if len(self.ranges) != len(other.ranges):
            return False
        return all(r == o for r, o in zip(self.ranges, other.ranges))

    def __gt__(self, other: int) -> bool:
        return other < min(r.start for r in self.ranges)

    def __ge__(self, other: int) -> bool:
        return other <= max(r.end for r in self.ranges)

    def __lt__(self, other: int) -> bool:
        return other > max(r.end for r in self.ranges)

    def __le__(self, other: int) -> bool:
        return other >= min(r.start for r in self.ranges)

    def __hash__(self) -> int:
        return hash(("Ranges", tuple(self.ranges)))

    def __copy__(self) -> Ranges:
        return Ranges(*self.ranges)

    def copy(self) -> Ranges:
        return self.__copy__()

    def __deepcopy__(self, memo: dict | None) -> Ranges:
        return Ranges(*[Range(r) for r in self.ranges])

    def deepcopy(self) -> Ranges:
        return self.__deepcopy__(None)

    def __reduce__(self) -> tuple[type[Ranges], tuple[tuple[Range, ...]]]:
        return (Ranges, (tuple(self.ranges),))

    def __add__(self, other: int) -> Ranges:
        return Ranges(*(r + other for r in self.ranges))

    def __radd__(self, other: int) -> Ranges:
        return Ranges(*(other + r for r in self.ranges))

    def __sub__(self, other: int) -> Ranges:
        return self.__add__(-other)

    def __rsub__(self, other: int) -> Ranges:
        return self.__radd__(-other)

    def __iadd__(self, other: int) -> None:
        for i, r in enumerate(self.ranges):
            self.ranges[i] = r + other

    def __isub__(self, other: int) -> None:
        self.__iadd__(-other)

    def __and__(self, other: int | range | slice | Range) -> Range | Ranges:
        result: list[Range] = []
        other_ = Range(int(other), int(other) + 1) if isinstance(other, int) else Range(other)

        for r in self.ranges:
            range_ = r & other_
            if range_:
                result.append(range_)

        result_ = Ranges(*result)
        if not result_:
            return EmptyRange()
        if len(result_.ranges) == 1:
            return result_.ranges[0]
        return result_

    def __or__(self, other: int | range | slice | Range | Ranges) -> Range | Ranges:
        if isinstance(other, Ranges):
            return Ranges(*self.ranges, *other.ranges)

        other_ = Range(int(other), int(other) + 1) if isinstance(other, int) else Range(other)
        result_ = Ranges(*self.ranges, other_)

        if not result_:
            return EmptyRange()
        if len(result_.ranges) == 1:
            return result_.ranges[0]
        return result_

    def __ror__(self, other: int | range | slice | Range | Ranges) -> Range | Ranges:
        return self.__or__(other)

    def __int__(self) -> int:
        if len(self) != 1:
            raise ValueError(f"cannot convert range with length {len(self)} to int")
        return self[0]

    def split(self, value: int) -> tuple[Range | Ranges, Range | Ranges]:
        idx = self.index_near(value)
        return self[:idx], self[idx:]
