# note: code may have been written in a rush, here be dragons and lots of bad patterns to avoid.
import functools
import itertools
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
