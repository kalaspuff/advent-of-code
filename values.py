from __future__ import annotations

import re
from typing import (
    Any,
    Callable,
    Generic,
    GenericAlias,
    Iterable,
    List,
    Optional,
    ParamSpec,
    Protocol,
    TypeVar,
    TypeVarTuple,
    Union,
    Unpack,
    overload,
)

from helpers import group_rows, match_rows
from matrix import Matrix

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")

Ts = TypeVarTuple("Ts")


P = ParamSpec("P")
R = TypeVar("R")
C = TypeVar("C", bound=Callable)

# CallableTuple = tuple[Callable[..., T], ...]


# class GenericAlias_(GenericAlias):
#     pass


# class CallableT(Protocol[C]):
#     def __class_getitem__(cls, item: Callable[P, T]):
#         return GenericAlias_(cls, item)
#
#     def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
#         return self.__orig_class__.__args__[0]


class Values:
    def __init__(self) -> None:
        self.attrs: List[str] = ["year", "day", "part", "input_filename"]
        self.input_: str = ""
        self.result: List[Any] = []
        self.counter: int = 0
        self.year: int
        self.day: int
        self.part: int
        self.input_filename: str
        self._rows: List[str]
        self._int_rows: List[int]
        self._csv: List[str]
        self._int_csv: List[int]
        self._matrix: Matrix

    def __setattr__(self, key: str, value: Any) -> None:
        super().__setattr__(key, value)
        if key not in ("attrs", "input_") and not key.startswith("_") and key not in self.attrs:
            if key == "counter" and value == 0:
                return
            self.attrs.append(key)

    def split(self, split_value: str) -> List[str]:
        return self.input_.split(split_value)

    def match(self, regexp: str, transform: Optional[Union[tuple[Any, ...], List[Any]]] = None) -> Any:
        return match_rows([self.input_], regexp, transform=transform)[0]

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
        self, regexp: str, transform: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3], Callable[..., T4]]
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

    # @overload
    # def match_rows(self, regexp: str, transform: tuple[Callable[..., Any], ...]) -> list[tuple[Any]]:
    #    ...

    @overload
    def match_rows(self, regexp: str, transform: list[Callable[..., T]]) -> list[tuple[T, ...]]:
        ...

    # @overload
    # def match_rows(
    #     self,
    #     regexp: str,
    #     transform: CallableTuple[Any],
    # ) -> list[Iterable[*Ts]]:
    #     ...

    @overload
    def match_rows(self, regexp: str, transform: None) -> list[tuple[Any, ...]]:
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
                Iterable[Callable[..., Any]],
                list[Callable[..., Any]],
            ]
        ] = None,
    ) -> list[Any]:
        return match_rows(self.rows, regexp, transform=transform)

    def grouped_rows(self, *, split: str = "", transform: Optional[Callable] = None) -> List[List[str]]:
        return group_rows(self.rows, split=split, transform=transform)

    def group_rows(self, *, split: str = "", transform: Optional[Callable] = None) -> List[List[str]]:
        return self.grouped_rows(split=split, transform=transform)

    @property
    def input(self) -> str:
        return self.input_

    @property
    def rows(self) -> List[str]:
        if getattr(self, "_rows", None) is None:
            self._rows = self.input_.split("\n")
        return self._rows

    @property
    def input_rows(self) -> List[str]:
        return self.rows

    @property
    def int_rows(self) -> List[int]:
        if getattr(self, "_int_rows", None) is None:
            self._int_rows = list(map(int, self.rows))
        return self._int_rows

    @property
    def rows_int(self) -> List[int]:
        return self.int_rows

    @property
    def input_int_rows(self) -> List[int]:
        return self.int_rows

    @property
    def csv(self) -> List[str]:
        if getattr(self, "_csv", None) is None:
            self._csv = self.input_.split(",")
        return self._csv

    @property
    def input_csv(self) -> List[str]:
        return self.csv

    @property
    def int_csv(self) -> List[int]:
        if getattr(self, "_int_csv", None) is None:
            self._int_csv = list(map(int, self.csv))
        return self._int_csv

    @property
    def csv_int(self) -> List[int]:
        return self.int_csv

    @property
    def matrix(self) -> Matrix:
        if getattr(self, "_matrix", None) is None:
            self._matrix = Matrix(self.rows)
        return self._matrix

    @property
    def input_basename(self) -> str:
        import os

        return os.path.basename(self.input_filename)


values = Values()
