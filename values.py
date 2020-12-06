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

    def __setattr__(self, key: str, value: Any) -> None:
        super().__setattr__(key, value)
        if key not in ("attrs", "input_") and key not in self.attrs:
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
        return self.input_.split("\n")

    @property
    def input_rows(self) -> List[str]:
        return self.rows

    @property
    def int_rows(self) -> List[int]:
        return list(map(int, self.rows))

    @property
    def input_int_rows(self) -> List[int]:
        return self.int_rows

    @property
    def matrix(self) -> Matrix:
        return Matrix(self.rows)


values = Values()
