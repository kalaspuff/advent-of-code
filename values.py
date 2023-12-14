# note: code may have been written in a rush, here be dragons and lots of bad patterns to avoid.

from __future__ import annotations

import inspect
import itertools
import re
import weakref
from abc import ABCMeta, abstractmethod
from collections import deque
from types import GenericAlias as _GenericAlias
from typing import (
    Any,
    Callable,
    Collection,
    Generic,
    Iterable,
    Iterator,
    Optional,
    ParamSpec,
    Protocol,
    Reversible,
    Self,
    Sequence,
    SupportsIndex,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from helpers import batched, findall_rows, group_rows, match_rows, paired, pairwise

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")

P = ParamSpec("P")
R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)
C = TypeVar("C", bound=Callable)
C_co = TypeVar("C_co", bound=Callable, covariant=True)

# CallableTuple = tuple[Callable[..., T], ...]


class GenericAlias(Protocol[C_co]):
    def __class_getitem__(cls, item: Union[R, tuple[R, ...]]) -> type[CallableT[R]]:
        if not isinstance(item, tuple):
            item = (item,)
        # return CallableT()
        result = type(
            f"CallableT{item}",
            (cls,),
            {
                "__args__": item,
                "__qualname__": f'CallableT[{", ".join(arg.__name__ for arg in item)}]',
                "__module__": "values",
                "__repr__": lambda self: f"CallableT{item}",
                "__func__": item,
                "__orig_class__": cls,
            },
        )
        return cast("type[CallableT[R]]", result)
        # return cast(Callable[..., R], type(f"CallableT{return_type}", (cls,), {"__args__": return_type}))

    # def __repr__(self):
    #     args = self.__args__ if isinstance(self.__args__, tuple) else (self.__args__,)
    #     return f'CallableT[{", ".join(arg.__name__ for arg in args)}]'

    # def __str__(self):
    #     args = self.__args__ if isinstance(self.__args__, tuple) else (self.__args__,)
    #     return f'CallableT[{", ".join(arg.__name__ for arg in args)}]'


# class CallableT:
#     def __getitem__(self, item: Callable[P, T]) -> GenericAlias[Callable, P, T]:
#         ...
#
#     def __class_getitem__(cls, item: Callable[P, T]):
#         return GenericAlias(cls, item)
#
#     def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
#         return self.__orig_class__.__args__[0]  # type: ignore[attr-defined]


# class CallableTMeta(ABCMeta):
#    def __getitem__(cls, item) -> CallableT:
#        return type("CallableT", (CallableT,), {"__return_type__": item})


# class CallableTMeta(GenericAlias):
#    def __getitem__(cls, item):
#        return type(f"CallableT[{item.__name__}]", (cls,), {"__return_type__": item})


class CallableTMeta(ABCMeta):
    def __getitem__(cls, return_type):
        if not isinstance(return_type, tuple):
            return_type = (return_type,)
        return type(f"CallableT{return_type}", (cls,), {"__args__": return_type})


# Define the CallableT class with Generic
class CallableT(GenericAlias[Callable[..., R]]):
    __orig_class__: CallableT
    __args__: R
    # __return_type__: type[R]

    # def __repr__(self) -> str:
    #    return f"CallableT[{self.__return_type__.__name__}]"
    #    # return "CallableT"

    def __repr__(self):
        if not hasattr(self, "__args__") or not self.__args__:
            return "CallableT"
        args = self.__args__ if isinstance(self.__args__, tuple) else (self.__args__,)
        return f'CallableT[{", ".join(arg.__name__ for arg in args)}]'

    def __str__(self):
        if not hasattr(self, "__args__") or not self.__args__:
            return "CallableT"
        args = self.__args__ if isinstance(self.__args__, tuple) else (self.__args__,)
        return f'CallableT[{", ".join(arg.__name__ for arg in args)}]'

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        # if not hasattr(self, "__args__") or not self.__args__:
        #     return self.__orig_class__.__args__[0](*args, **kwargs)  # type: ignore[attr-defined]
        return self.__args__[0](*args, **kwargs)  # type: ignore[attr-defined]

    # @abstractmethod
    # def __call__(self, *args, **kwargs) -> T:
    #     raise NotImplementedError

    # # def __class_getitem__(cls, item: Union[R, tuple[R, ...]]) -> CallableT[P, R]:
    #     return super().__class_getitem__(item)


class _AssignableValue:
    def __init__(self, value=None):
        self.value = value


class Assignable:
    _assignments = {}

    def __new__(self, value=None):
        print("NEW", self, value)
        instance = super().__new__(self)
        print(instance)
        return instance

    def __init__(self, value=None):
        self.value = value
        print("INIT", self, value)
        self._weakref = weakref.ref(self)
        weakref.finalize(self, Assignable._on_finalize, weakref.ref(self))

    @classmethod
    def _on_finalize(cls, value):
        print("ON FINALIZE", cls, value)
        return
        for var_name, ref in Assignable._assignments.items():
            if ref() is None:
                print("GARBAGE COLLECTED", ref, var_name)
                # garbage collected
                frame = inspect.currentframe()
                try:
                    frame.f_back.f_locals[var_name] = Assignable(value)
                    print("FRAME", frame.f_back.f_locals)
                finally:
                    del frame
                break

    def __repr__(self):
        if not hasattr(self, "value"):
            return "Assignable"
        return f"Assignable({self.value})"


def assign(name: str, value: Any) -> None:
    frame = inspect.currentframe()
    try:
        frame.f_back.f_locals[name] = value
        Assignable._assignments[name] = weakref.ref(value)
    finally:
        del frame


# some_variable = Assignable()
# print("A 1", some_variable)
# some_variable = "test"
# print("A 2", some_variable)
#
# assign("some_variable", Assignable())
# print("B 1", some_variable)
# some_variable = "test"
# print("B 2", some_variable)
#
# import sys
#
# sys.exit(0)

ValuesIntT = TypeVar("ValuesIntT", "ValuesRow", "Values[str, str]", str)
ValuesSliceT = TypeVar("ValuesSliceT", "Values[ValuesRow, ValuesSlice]", "ValuesSlice", str)


class Values(Generic[ValuesIntT, ValuesSliceT]):
    def __new__(cls, *input_: AcceptedTypes) -> ValuesSlice:
        instance = super().__new__(cls)
        return cast(ValuesSlice, instance)

    def __init__(self, *input_: AcceptedTypes) -> None:
        self.attrs: list[str] = ["year", "day", "part", "input_filename", "elapsed_time"]
        self.input_: str = ""
        self.result: Any = []
        self.counter: int = 0
        self.year: int
        self.day: int
        self.part: int
        self.input_filename: str
        self._rows: list[str]
        self._int_rows: list[int]
        self._csv: list[str]
        self._int_csv: list[int]
        self._matrix: Matrix
        self._origin: Optional[Values] = None
        self._index: Optional[int] = None
        self._row_index: Optional[int] = None
        self._slice: Optional[slice] = None
        self._next_slice: Optional[slice] = None
        self._single_row: bool = False
        self._starred_assignment: Optional[Values] = None
        self._iter_returned: Optional[list[Any]] = None
        self._origin_iterator: Optional[Values] = None
        self._sized: bool = True
        self._reversed: bool = False

        if input_:
            if isinstance(input_, str):
                self.input_ = input_
            elif isinstance(input_, Values):
                self.input_ = input_.input
            elif isinstance(input_, (list, tuple, deque, Sequence)):
                if isinstance(input_, (list, tuple, deque, Sequence)) and len(input_) == 1:
                    input_ = input_[0]
                if isinstance(input_, (Values, str)):
                    input_ = (input_,)
                if isinstance(input_, (deque,)) and input_ and isinstance(input_[0], (deque,)):
                    input_ = tuple(
                        "".join(row_data) if isinstance(row_data, str) else "".join([Values(x).input for x in row_data])
                        for row_data in input_
                    )
                rows: list[str] = []
                for row_data in input_:
                    if isinstance(row_data, int):
                        continue
                    if isinstance(row_data, str):
                        rows.extend(row_data.split("\n"))
                    elif isinstance(row_data, Values):
                        rows.extend(row_data.input.split("\n"))
                    else:
                        rows.extend(Values(row_data).input_.split("\n"))
                self.input_ = "\n".join(rows)
        self._rows = self.input_.split("\n")

    @classmethod
    def create_rows(cls, row_count: int) -> Values:
        return Values() * row_count

    def __setattr__(self, key: str, value: Any) -> None:
        super().__setattr__(key, value)
        if key not in ("attrs", "input_") and not key.startswith("_") and key not in self.attrs:
            if key == "counter" and value == 0:
                return
            self.attrs.append(key)

    # def __class_getitem__(cls, item: type[T]) -> Values[type[T]]:
    #     return Values[type[T]]

    @overload
    def __getitem__(self, value: int) -> ValuesIntT:
        ...

    @overload
    def __getitem__(self, value: slice) -> ValuesSliceT:
        ...

    def __getitem__(self, value: slice | int) -> ValuesRow | ValuesSlice | ValuesIntT | ValuesSliceT:
        try:
            if self._single_row and self._index is None:
                return cast(ValuesIntT, self.input[value])

            _ = self.rows[value]  # trigger IndexError if out of bounds
            values: ValuesRow | ValuesSlice  # ValuesRow | Values[ValuesRow, ValuesSlice]
            if isinstance(value, int):
                values = cast(ValuesRow, Values())
                values._single_row = True
            else:
                values = cast(ValuesSlice, Values())

            values._origin = self
            values._slice = value if isinstance(value, slice) else slice(value, (value + 1) if value != -1 else None)
            # if self._index is not None and isinstance(value, slice):
            # values._next_slice = slice(
            #     value.start - self._index, None if value.stop is None else value.stop - self._index, value.step
            # )
            # self._starred_assignment = values
            return values
        finally:
            self._sized = True

    def __len__(self) -> int:
        # if not self._sized:
        #    raise NotImplementedError
        if self._single_row:
            return len(self.input)
        return len(self.rows)

    def __str__(self) -> str:
        return str(self.input)

    def __int__(self) -> int:
        return int(self.input)

    def __iter__(self) -> Iterator[ValuesIntT]:
        iterator: Iterator[ValuesIntT] = cast(Iterator[ValuesIntT], self[self._index or 0 :])
        if isinstance(iterator, str):
            return iter(iterator)
        if not isinstance(iterator, Values):
            raise Exception("invalid iterator")
        iterator._origin_iterator = self
        iterator._sized = False
        iterator._index = 0
        iterator._iter_returned = []
        return iterator

    def iter(self) -> Iterator[ValuesIntT]:
        iterator: Iterator[ValuesIntT] = self.__iter__()
        return iterator

    def __next__(self: Values[ValuesIntT, ValuesSliceT]) -> ValuesIntT:
        self._sized = False
        if self._index is None:
            raise Exception("iterator is not initialized - initialize with iter(...)")

        _index = self._index
        if _index >= len(self.rows):
            # if self._starred_assignment:
            #     self._starred_assignment._next_slice = None
            #     self._starred_assignment = None
            # self._next_slice = None
            # print("***")
            # print(self._starred_assignment[-1])
            # print("***")
            # print(self._iter_returned)
            # print(self._origin_iterator._iter_returned)
            # print("***")
            # print("***")
            raise StopIteration
        # values: ValuesSlice | ValuesRow
        # if self._next_slice is not None:
        #    values = cast(ValuesSlice, self[self._next_slice])
        #    self._index = _index + len(values.rows)
        # else:
        values = cast(ValuesIntT, self[_index])
        self._index = _index + 1
        if self._iter_returned is not None:
            self._iter_returned.append(values)
        return values

    def next(self) -> ValuesIntT:
        return cast(ValuesIntT, next(self))

    def indices(
        self, sub: str | Values, start: Optional[SupportsIndex] = None, end: Optional[SupportsIndex] = None
    ) -> list[int]:
        index = start or 0
        indices = []
        while True:
            try:
                index = self.index(sub, index, end)
                indices.append(index)
                index = index + 1
            except ValueError:
                break
        return indices

    def pop(self, index: int = -1) -> ValuesIntT:
        if index is None:
            index = len(self) - 1
        if self._single_row:
            raise NotImplementedError("pop not implemented for single row values (strings)")
        if index < 0:
            index = len(self) + index
        if index >= len(self):
            raise IndexError("list assignment index out of range")
        if self._origin is not None and index != -1:
            raise NotImplementedError("pop from index not implemented for non origin values")
        rows = self.origin.rows
        row = rows.pop(self.row_index + index)
        self.origin.input_ = "\n".join(rows)
        values = cast(ValuesRow, Values(row))
        values._single_row = True
        self._recalc_input()
        return cast(ValuesIntT, values)

    def popleft(self) -> ValuesIntT:
        values = cast(ValuesRow, self.pop(0))
        return cast(ValuesIntT, values)

    def insert(self: ValuesSlice, index: int, other: AcceptedTypes) -> None:
        if self._origin is not None:
            raise NotImplementedError("append not implemented for non origin values")
        other = Values(other).input
        if "\n" in other:
            raise ValueError("insert only supports single row values")
        rows = self.origin.rows
        rows.insert(self.row_index + index, other)
        self.origin.input_ = "\n".join(rows)
        self._recalc_input()

    def append(self: ValuesSlice, other: AcceptedTypes) -> None:
        if self._origin is not None:
            raise NotImplementedError("append not implemented for non origin values")
        other = Values(other).input
        if "\n" in other:
            raise ValueError("append only supports single row values")
        rows = self.origin.rows
        rows.append(other)
        self.origin.input_ = "\n".join(rows)
        self._recalc_input()

    def extend(self: ValuesSlice, other: AcceptedTypes) -> None:
        self.append(other)

    def concat(self: ValuesRow, other: AcceptedTypes) -> ValuesRow:
        if "\n" in self.input:
            raise ValueError("concat only supports concatenation with values with single row")
        other = Values(other).input
        if "\n" in other:
            raise ValueError("concat only supports single row values")
        values = Values(self.input + other)
        values._single_row = True
        return cast(ValuesRow, values)

    def concat_rows(self, other: AcceptedTypes) -> ValuesSlice:
        values = self + Values(other)
        return cast(ValuesSlice, values)

    def transpose(self) -> ValuesSlice:
        max_len = max(len(row) for row in self.rows)
        values = Values.create_rows(max_len)
        for y, row in enumerate(self.new().rows):
            for x, char in enumerate(row):
                values[x][y] = char
        return cast(ValuesSlice, values)

    def rotate(self) -> ValuesSlice:
        return self.transpose()

    @overload
    def deque(self: ValuesSlice) -> deque[deque[str]]:
        ...

    @overload
    def deque(self: ValuesRow) -> deque[str]:
        ...

    def deque(self) -> deque[str] | deque[deque[str]]:
        if self._single_row or len(self.origin) == 1:
            return deque(self.input)
        return deque([deque(row) for row in self.new().rows])

    @overload
    def ints(self: ValuesSlice) -> list[tuple[int, ...]]:
        ...

    @overload
    def ints(self: ValuesRow) -> tuple[int, ...]:
        ...

    def ints(self) -> tuple[int, ...] | list[tuple[int, ...]]:
        if self._single_row or len(self.origin) == 1:
            return tuple(int(value) for value in re.findall(r"(?:^|[^0-9])(-?\d+)", self.input))
        return self.findall_ints()

    @overload
    def alphanums(self: ValuesSlice) -> list[tuple[str, ...]]:
        ...

    @overload
    def alphanums(self: ValuesRow) -> tuple[str, ...]:
        ...

    def alphanums(self) -> tuple[str, ...] | list[tuple[str, ...]]:
        if self._single_row or len(self.origin) == 1:
            return tuple(value for value in re.findall(r"([a-zA-Z0-9]+)", self.input))
        return self.findall_alphanums()

    @overload
    def words(self: ValuesSlice, words: tuple[str, ...] | list[str] | set[str]) -> list[tuple[str, ...]]:
        ...

    @overload
    def words(self: ValuesRow, words: tuple[str, ...] | list[str] | set[str]) -> tuple[str, ...]:
        ...

    def words(self, words: tuple[str, ...] | list[str] | set[str]) -> tuple[str, ...] | list[tuple[str, ...]]:
        if self._single_row or len(self.origin) == 1:
            words_regex = "|".join(words)
            return tuple(value for value in re.findall(rf"({words_regex})", self.input))
        return self.findall_words(words)

    @overload
    def digits(self: ValuesSlice) -> list[tuple[int, ...]]:
        ...

    @overload
    def digits(self: ValuesRow) -> tuple[int, ...]:
        ...

    def digits(self) -> tuple[int, ...] | list[tuple[int, ...]]:
        if self._single_row or len(self.origin) == 1:
            return tuple(int(value) for value in re.findall(r"(\d)", self.input))
        return self.findall_digits()

    @overload
    def split(
        self: ValuesSlice, sep: str | tuple[str, ...] | list[str] | set[str] = " ", maxsplit: int = -1
    ) -> list[tuple[str, ...]]:
        ...

    @overload
    def split(
        self: ValuesRow, sep: str | tuple[str, ...] | list[str] | set[str] = " ", maxsplit: int = -1
    ) -> tuple[str, ...]:
        ...

    def split(
        self, sep: str | tuple[str, ...] | list[str] | set[str] = " ", maxsplit: int = -1
    ) -> tuple[str, ...] | list[tuple[str, ...]]:
        if self._single_row or len(self.origin) == 1:
            return self.split_input(sep, maxsplit)
        return [value.split_input(sep, maxsplit) for value in values]

    @overload
    def split_values(
        self: ValuesSlice, sep: str | tuple[str, ...] | list[str] | set[str] = " ", maxsplit: int = -1
    ) -> list[ValuesSlice]:
        ...

    @overload
    def split_values(
        self: ValuesRow, sep: str | tuple[str, ...] | list[str] | set[str] = " ", maxsplit: int = -1
    ) -> ValuesSlice:
        ...

    def split_values(
        self, sep: str | tuple[str, ...] | list[str] | set[str] = " ", maxsplit: int = -1
    ) -> ValuesSlice | list[ValuesSlice]:
        if self._single_row or len(self.origin) == 1:
            return Values(self.split_input(sep, maxsplit))
        return [Values([v.strip() for v in value.split_input(sep, maxsplit)]) for value in values]

    def split_input(
        self, sep: str | tuple[str, ...] | list[str] | set[str] = " ", maxsplit: int = -1
    ) -> tuple[str, ...]:
        if isinstance(sep, (list, tuple, set)):
            parts = [self.input]
            for sep_ in sep:
                if sep_ in self.input:
                    parts_: list[str] = []
                    while parts:
                        part = parts.pop(0)
                        split_parts = part.split(sep_, maxsplit)
                        parts_.extend(split_parts)
                        if maxsplit != -1:
                            maxsplit -= len(split_parts)
                            if maxsplit < 0:
                                maxsplit = 0
                                break
                    parts_.extend(parts)
                    parts = parts_[:]
                    if maxsplit == 0:
                        break
            return tuple(parts)
        return tuple(self.input.split(sep, maxsplit))

    def split_sections(
        self, sep: str | tuple[str, ...] | list[str] | set[str] = " ", maxsplit: int = -1
    ) -> list[ValuesSlice]:
        return [Values(rows.strip()) for rows in self.split_input(sep, maxsplit)]

    def flatten(self) -> ValuesRow:
        values = Values("".join(self.new().rows))
        values._single_row = True
        return cast(ValuesRow, values)

    def join_by(self, by: str) -> ValuesRow:
        values = Values(by.join(self.new().rows))
        values._single_row = True
        return cast(ValuesRow, values)

    def join(self, by: str) -> ValuesRow:
        return self.join_by(by)

    def endswith(self, suffix: str) -> bool:
        return self.input.endswith(suffix)

    def startswith(self, prefix: str) -> bool:
        return self.input.startswith(prefix)

    def strip(self, chars: str | None = None) -> Self:
        values = Values(self.input.strip(chars))
        values._single_row = self._single_row
        return cast(Self, values)

    def __eq__(self, other: AcceptedTypes) -> bool:
        if isinstance(other, Values):
            return self is other or self.input == other.input
        return self.input == Values(other).input

    def __bool__(self) -> bool:
        return bool(self.input)

    def __add__(self, other: AcceptedTypes) -> ValuesSlice:
        return Values(self, other)

    def __radd__(self, other: AcceptedTypes) -> ValuesSlice:
        return Values(other, self)

    def __iadd__(self, other: AcceptedTypes) -> ValuesSlice:
        return Values(self, other)

    def __mul__(self, value: int) -> ValuesSlice:
        return Values(*[self for _ in range(value)])

    def __delitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key: slice | int, value):
        if self._single_row:
            row = cast(ValuesRow, self).rows[0]
            if isinstance(key, int) and len(value) > 1:
                raise ValueError("single key assignment with non-single string value (use slice assignment instead)")
            from_ = key.start if isinstance(key, slice) else key
            to_ = min(
                (key.stop or from_ + len(value)) if isinstance(key, slice) else (from_ + key + 1), from_ + len(value)
            )
            if to_ - from_ < len(value):
                value = value[: to_ - from_]
            prepend = ""
            if len(row[:from_]) < from_:
                prepend = " " * (from_ - len(row[:from_]))
            new_row = row[:from_] + prepend + value + row[to_:]
            self.origin._rows[self.row_index] = new_row
        else:
            if isinstance(key, slice):
                raise NotImplementedError("slice assignment not implemented")
            if key < 0:
                key = len(self) + key
            if key >= len(self):
                raise IndexError("list assignment index out of range")
            self.origin._rows[self.row_index + key] = value
        self.origin.input_ = "\n".join(self.origin._rows)
        self._recalc_input()

    def _recalc_input(self) -> None:
        self.origin._rows = self.origin.input_.split("\n")

    def __reversed__(self) -> Self:
        values = self.__copy__()
        values._slice = slice(None, None, -1)
        values._reversed = not self._reversed
        return values

    def reversed(self) -> Self:
        return self.__reversed__()

    def __contains__(self, item: str | int) -> bool:
        item_ = str(item)
        return item_ in self.input if self._single_row else item_ in self.new().rows

    def __copy__(self) -> Self:
        values = cast(Self, Values())
        values._origin = self
        values._reversed = self._reversed
        values._single_row = self._single_row
        return values

    def copy(self) -> Self:
        return self.__copy__()

    def __deepcopy__(self, memo: dict) -> Self:
        values = cast(Self, Values(self.input))
        values._single_row = self._single_row
        # values._rows = self.rows[:: -1 if self._reversed else 1]
        # values.input_ = self.input[:: -1 if self._reversed else 1]
        if self._reversed:
            values._reversed = self._reversed
            values._slice = slice(None, None, -1)
        return values

    def deepcopy(self) -> Self:
        return self.__deepcopy__(None)

    def count(
        self, sub: str | Values, start: Optional[SupportsIndex] = None, end: Optional[SupportsIndex] = None
    ) -> int:
        if isinstance(sub, Values):
            sub = sub.input
        if self._single_row:
            return self.input.count(sub, start, end)

        # end = min(int(cast(int, end or len(self.rows))), len(self.rows))
        # start = int(cast(int, start or 0))
        return len(self.indices(sub, start, end))
        # for i in range(start, end):
        #     if self.rows[i] == sub:
        #         count += 1
        # return count

    def index(
        self, sub: str | ValuesRow, start: Optional[SupportsIndex] = None, end: Optional[SupportsIndex] = None
    ) -> int:
        if isinstance(sub, Values):
            sub = sub.input
        if self._single_row:
            return self.input.index(sub, start, end)

        end = end if end is not None else len(self.rows)  # min(int(cast(int, end or len(self.rows))), len(self.rows))
        start = start or 0  # int(cast(int, start or 0))
        return self.new().rows.index(sub, start, end)
        # for i in range(start, end):
        #     if self.rows[i] == sub:
        #         return i
        # raise ValueError("substring not found")

    def seek(self, index: int) -> Self:
        self._index = index
        return self

    def reset(self) -> Self:
        self.seek(0)
        return self

    def match(self, regexp: str, transform: Optional[Union[tuple[Any, ...], list[Any]]] = None) -> Any:
        return match_rows([self.input], regexp, transform=transform)[0]

    @overload
    def match_rows(self, regexp: str, transform: tuple[Callable[..., T1]]) -> list[tuple[T1]]:
        ...

    @overload
    def match_rows(self, regexp: str, transform: tuple[Callable[..., T1], Callable[..., T2]]) -> list[tuple[T1, T2]]:
        ...

    @overload
    def match_rows(
        self, regexp: str, transform: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3]]
    ) -> list[tuple[T1, T2, T3]]:
        ...

    @overload
    def match_rows(
        self,
        regexp: str,
        transform: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3], Callable[..., T4]],
    ) -> list[tuple[T1, T2, T3, T4]]:
        ...

    @overload
    def match_rows(
        self,
        regexp: str,
        transform: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3], Callable[..., T4], Callable[..., T5]],
    ) -> list[tuple[T1, T2, T3, T4, T5]]:
        ...

    @overload
    def match_rows(
        self,
        regexp: str,
        transform: tuple[
            Callable[..., T1],
            Callable[..., T2],
            Callable[..., T3],
            Callable[..., T4],
            Callable[..., T5],
            Callable[..., T6],
        ],
    ) -> list[tuple[T1, T2, T3, T4, T5, T6]]:
        ...

    @overload
    def match_rows(
        self,
        regexp: str,
        transform: tuple[
            Callable[..., T],
            Callable[..., T],
            Callable[..., T],
            Callable[..., T],
            Callable[..., T],
            Callable[..., T],
            *tuple[Callable[..., T], ...],
        ],
    ) -> list[tuple[T, ...]]:
        ...

    @overload
    def match_rows(self, regexp: str, transform: Callable[..., T]) -> list[tuple[T, ...]]:
        ...

    @overload
    def match_rows(self, regexp: str, transform: list[Callable[..., T]]) -> list[tuple[T, ...]]:
        ...

    @overload
    def match_rows(self, regexp: str, transform: None = None) -> list[tuple[Any, ...]]:
        ...

    def match_rows(
        self,
        regexp: str,
        transform: Optional[
            Union[
                tuple[Callable[..., Any]],
                tuple[Callable[..., Any], Callable[..., Any]],
                tuple[Callable[..., Any], Callable[..., Any], Callable[..., Any]],
                tuple[Callable[..., Any], Callable[..., Any], Callable[..., Any], Callable[..., Any]],
                tuple[
                    Callable[..., Any], Callable[..., Any], Callable[..., Any], Callable[..., Any], Callable[..., Any]
                ],
                tuple[
                    Callable[..., Any],
                    Callable[..., Any],
                    Callable[..., Any],
                    Callable[..., Any],
                    Callable[..., Any],
                    Callable[..., Any],
                ],
                tuple[Callable[..., Any], ...],
                Callable[..., T],
                Iterable[Callable[..., Any]],
                list[Callable[..., Any]],
            ]
        ] = None,
    ) -> list[Any]:
        transform_ = tuple(transform) if isinstance(transform, (tuple, list, Iterable)) else transform
        return match_rows(self.new().rows, regexp, transform=transform_)

    @overload
    def findall_rows(self, regexp: str, transform: tuple[Callable[..., T1]]) -> list[tuple[T1]]:
        ...

    @overload
    def findall_rows(self, regexp: str, transform: tuple[Callable[..., T1], Callable[..., T2]]) -> list[tuple[T1, T2]]:
        ...

    @overload
    def findall_rows(
        self, regexp: str, transform: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3]]
    ) -> list[tuple[T1, T2, T3]]:
        ...

    @overload
    def findall_rows(
        self,
        regexp: str,
        transform: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3], Callable[..., T4]],
    ) -> list[tuple[T1, T2, T3, T4]]:
        ...

    @overload
    def findall_rows(
        self,
        regexp: str,
        transform: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3], Callable[..., T4], Callable[..., T5]],
    ) -> list[tuple[T1, T2, T3, T4, T5]]:
        ...

    @overload
    def findall_rows(
        self,
        regexp: str,
        transform: tuple[
            Callable[..., T1],
            Callable[..., T2],
            Callable[..., T3],
            Callable[..., T4],
            Callable[..., T5],
            Callable[..., T6],
        ],
    ) -> list[tuple[T1, T2, T3, T4, T5, T6]]:
        ...

    @overload
    def findall_rows(
        self,
        regexp: str,
        transform: tuple[
            Callable[..., T],
            Callable[..., T],
            Callable[..., T],
            Callable[..., T],
            Callable[..., T],
            Callable[..., T],
            *tuple[Callable[..., T], ...],
        ],
    ) -> list[tuple[T, ...]]:
        ...

    @overload
    def findall_rows(self, regexp: str, transform: Callable[..., T]) -> list[tuple[T, ...]]:
        ...

    @overload
    def findall_rows(self, regexp: str, transform: list[Callable[..., T]]) -> list[tuple[T, ...]]:
        ...

    @overload
    def findall_rows(self, regexp: str, transform: None = None) -> list[tuple[Any, ...]]:
        ...

    def findall_rows(
        self,
        regexp: str,
        transform: Optional[
            Union[
                tuple[Callable[..., Any]],
                tuple[Callable[..., Any], Callable[..., Any]],
                tuple[Callable[..., Any], Callable[..., Any], Callable[..., Any]],
                tuple[Callable[..., Any], Callable[..., Any], Callable[..., Any], Callable[..., Any]],
                tuple[
                    Callable[..., Any], Callable[..., Any], Callable[..., Any], Callable[..., Any], Callable[..., Any]
                ],
                tuple[
                    Callable[..., Any],
                    Callable[..., Any],
                    Callable[..., Any],
                    Callable[..., Any],
                    Callable[..., Any],
                    Callable[..., Any],
                ],
                tuple[Callable[..., Any], ...],
                Callable[..., T],
                Iterable[Callable[..., Any]],
                list[Callable[..., Any]],
            ]
        ] = None,
    ) -> list[Any]:
        transform_ = tuple(transform) if isinstance(transform, (tuple, list, Iterable)) else transform
        return findall_rows(self.new().rows, regexp, transform=transform_)

    def findall_ints(self) -> list[tuple[int, ...]]:
        return self.findall_rows(r"(?:^|[^0-9])(-?\d+)", transform=int)

    def findall_int(self) -> list[tuple[int, ...]]:
        return self.findall_ints()

    def findall_digits(self) -> list[tuple[int, ...]]:
        return self.findall_rows(r"(\d)", int)

    def findall_words(self, words: tuple[str, ...] | list[str] | set[str]) -> list[tuple[str, ...]]:
        words_regex = "|".join(words)
        return self.findall_rows(rf"({words_regex})", transform=str)

    def findall_alphanums(self) -> list[tuple[str, ...]]:
        return self.findall_rows(r"([a-zA-Z0-9]+)", transform=str)

    def findall_alphanum(self) -> list[tuple[str, ...]]:
        return self.findall_alphanums()

    def findall_alpha(self) -> list[tuple[str, ...]]:
        return self.findall_alphanums()

    def grouped_rows(self, *, split: str = "", transform: Optional[Callable] = None) -> list[list[str]]:
        return group_rows(self.rows, split=split, transform=transform)

    def group_rows(self, *, split: str = "", transform: Optional[Callable] = None) -> list[list[str]]:
        return self.grouped_rows(split=split, transform=transform)

    def pairwise(self) -> list[tuple[Any, Any]]:
        return pairwise(self.rows)

    def batched(self, n) -> list[tuple[Any, ...]]:
        return batched(self.rows, n)

    def paired(self) -> list[tuple[Any, Any]]:
        return paired(self.rows)

    def new(self) -> Self:
        return Values(self.input)

    @property
    def input(self) -> str:
        value = "\n".join(self.rows[::-1] if self._reversed else self.rows) if self._origin is not None else self.input_
        return value[::-1] if self._reversed else value

    @property
    def data(self) -> str:
        return self.input

    @property
    def value(self) -> str:
        return self.input

    @property
    def content(self) -> str:
        return self.input

    @property
    def body(self) -> str:
        return self.input

    @property
    def rows(self) -> list[str]:
        if self._origin is not None:
            if self._slice is not None:
                return self._origin.rows[self._slice]
            return self._origin.rows
        if getattr(self, "_rows", None) is None:
            self._rows = self.input.split("\n")
        if self._slice:
            return self._rows[self._slice]
        return self._rows

    @property
    def lines(self) -> list[str]:
        return self.rows

    @property
    def input_rows(self) -> list[str]:
        return self.rows

    @property
    def int_rows(self) -> list[int]:
        if getattr(self, "_int_rows", None) is None:
            self._int_rows = list(map(int, self.new().rows))
        return self._int_rows

    @property
    def rows_int(self) -> list[int]:
        return self.int_rows

    @property
    def input_int_rows(self) -> list[int]:
        return self.int_rows

    @property
    def csv(self) -> list[str]:
        if getattr(self, "_csv", None) is None:
            self._csv = self.input.split(",")
        return self._csv

    @property
    def input_csv(self) -> list[str]:
        return self.csv

    @property
    def int_csv(self) -> list[int]:
        if getattr(self, "_int_csv", None) is None:
            self._int_csv = list(map(int, self.csv))
        return self._int_csv

    @property
    def csv_int(self) -> list[int]:
        return self.int_csv

    @property
    def matrix(self) -> Matrix:
        if getattr(self, "_matrix", None) is None:
            self._matrix = Matrix(self.new().rows)
        return self._matrix

    @property
    def origin(self) -> Values:
        return self._origin if self._origin is not None else self

    @property
    def row_index(self) -> int:
        origin_index = self._origin.row_index if self._origin is not None else 0
        index = self._slice.start if self._slice else 0
        return origin_index + index

    @property
    def line_index(self) -> int:
        return self.row_index

    @property
    def n(self) -> int:
        return self.row_index

    @property
    def i(self) -> int:
        return self.row_index

    @property
    def input_basename(self) -> str:
        import os

        return os.path.basename(self.input_filename)


Sequence.register(Values)
Iterable.register(Values)
Iterator.register(Values)
Collection.register(Values)
Reversible.register(Values)


ValuesRow = Values[str, str]
ValuesSlice = Values[ValuesRow, "ValuesSlice"]

AcceptedTypes = (
    str
    | list["AcceptedTypes"]
    | tuple["AcceptedTypes", ...]
    | deque["AcceptedTypes"]
    | Sequence["AcceptedTypes"]
    | Iterator["AcceptedTypes"]
    | ValuesRow
    | ValuesSlice
    | Values[Any, Any]
    | Values
)

values: ValuesSlice = Values()

from matrix import Matrix  # noqa: E402


# Some Regular expression examples:
#
# Positive Integers:
#
# ^\d+$
# Negative Integers:
#
# ^-\d+$
# Integer:
#
# ^-?\d+$
# Positive Number:
#
# ^\d*\.?\d+$
# Negative Number:
#
# ^-\d*\.?\d+$
# Positive Number or Negative Number:
#
# ^-?\d*\.{0,1}\d+$
# Phone number:
#
# ^\+?[\d\s]{3,}$
# Phone with code:
#
# ^\+?[\d\s]+\(?[\d\s]{10,}$
# Year 1900-2099:
#
# ^(19|20)[\d]{2,2}$
# Date (dd mm yyyy, d/m/yyyy, etc.):
#
# ^([1-9]|0[1-9]|[12][0-9]|3[01])\D([1-9]|0[1-9]|1[012])\D(19[0-9][0-9]|20[0-9][0-9])$
# IP v4:
#
# ^(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]){3}$
