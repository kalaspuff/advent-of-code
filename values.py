# note: code may have been written in a rush, here be dragons and lots of bad patterns to avoid.

from __future__ import annotations

import inspect
import weakref
from abc import ABCMeta, abstractmethod
from types import GenericAlias as _GenericAlias
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Optional,
    ParamSpec,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from helpers import findall_rows, group_rows, match_rows
from matrix import Matrix

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


class Values:
    def __init__(self) -> None:
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

    def __setattr__(self, key: str, value: Any) -> None:
        super().__setattr__(key, value)
        if key not in ("attrs", "input_") and not key.startswith("_") and key not in self.attrs:
            if key == "counter" and value == 0:
                return
            self.attrs.append(key)

    def split(self, split_value: str) -> list[str]:
        return self.input_.split(split_value)

    def match(self, regexp: str, transform: Optional[Union[tuple[Any, ...], list[Any]]] = None) -> Any:
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
    def match_rows(
        self,
        regexp: str,
        transform: Callable[..., T],
    ) -> list[tuple[T, ...]]:
        ...

    @overload
    def match_rows(self, regexp: str, transform: list[Callable[..., T]]) -> list[tuple[T, ...]]:
        ...

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
                Callable[..., T],
                Iterable[Callable[..., Any]],
                list[Callable[..., Any]],
            ]
        ] = None,
    ) -> list[Any]:
        transform_ = tuple(transform) if isinstance(transform, (tuple, list, Iterable)) else transform
        return match_rows(self.rows, regexp, transform=transform_)

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
        self, regexp: str, transform: tuple[Callable[..., T1], Callable[..., T2], Callable[..., T3], Callable[..., T4]]
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
    def findall_rows(
        self,
        regexp: str,
        transform: Callable[..., T],
    ) -> list[tuple[T, ...]]:
        ...

    @overload
    def findall_rows(self, regexp: str, transform: list[Callable[..., T]]) -> list[tuple[T, ...]]:
        ...

    @overload
    def findall_rows(self, regexp: str, transform: None) -> list[tuple[Any, ...]]:
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
        return findall_rows(self.rows, regexp, transform=transform_)

    def grouped_rows(self, *, split: str = "", transform: Optional[Callable] = None) -> list[list[str]]:
        return group_rows(self.rows, split=split, transform=transform)

    def group_rows(self, *, split: str = "", transform: Optional[Callable] = None) -> list[list[str]]:
        return self.grouped_rows(split=split, transform=transform)

    @property
    def input(self) -> str:
        return self.input_

    @property
    def rows(self) -> list[str]:
        if getattr(self, "_rows", None) is None:
            self._rows = self.input_.split("\n")
        return self._rows

    @property
    def input_rows(self) -> list[str]:
        return self.rows

    @property
    def int_rows(self) -> list[int]:
        if getattr(self, "_int_rows", None) is None:
            self._int_rows = list(map(int, self.rows))
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
            self._csv = self.input_.split(",")
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
            self._matrix = Matrix(self.rows)
        return self._matrix

    @property
    def input_basename(self) -> str:
        import os

        return os.path.basename(self.input_filename)


values = Values()
