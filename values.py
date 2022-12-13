import re
from typing import Any, Callable, List, Optional, Tuple, Union

from helpers import group_rows, match_rows
from matrix import Matrix


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

    def match(self, regexp: str, transform: Optional[Union[Tuple[Any, ...], List[Any]]] = None) -> Any:
        return match_rows([self.input_], regexp, transform=transform)[0]

    def match_rows(self, regexp: str, transform: Optional[Union[Tuple[Any, ...], List[Any]]] = None) -> Any:
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


values = Values()
