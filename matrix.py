# note: code may have been written in a rush, here be dragons and lots of bad patterns to avoid.
from __future__ import annotations

import re
from typing import (
    Annotated,
    Any,
    ClassVar,
    Generic,
    Iterable,
    Literal,
    Optional,
    Protocol,
    TypeAlias,
    TypeVar,
    Unpack,
    cast,
    overload,
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class DEFAULT(Generic[T]):
    __args__: tuple[()] | tuple[T]
    __singleton__: Optional[DefaultValue] = None
    __init_singleton__: bool = False

    @overload
    def __new__(cls, item: Literal[False]) -> DEFAULT[Literal[False]]:
        ...

    @overload
    def __new__(cls, item: Literal[True]) -> DEFAULT[Literal[True]]:
        ...

    @overload
    def __new__(cls, item: Literal[None]) -> DEFAULT[Literal[None]]:
        ...

    @overload
    def __new__(cls, item: type[T]) -> DEFAULT[type[T]]:
        ...

    @overload
    def __new__(cls, item: T) -> DEFAULT[T]:
        ...

    @overload
    def __new__(cls) -> DefaultValue:
        ...

    def __new__(cls, item: Any = None) -> Any:
        if item is None:
            return super().__new__(cls)
        cls.__args__ = (item,) if item else ()
        return item

    @overload
    def __eq__(
        self: DEFAULT[Literal[True]] | Literal[True], other: DEFAULT[Literal[True]] | Literal[True]
    ) -> Literal[True]:
        ...

    @overload
    def __eq__(
        self: DEFAULT[Literal[False]] | Literal[False], other: DEFAULT[Literal[False]] | Literal[False]
    ) -> Literal[True]:
        ...

    @overload
    def __eq__(self, other: T | DEFAULT[T]) -> Literal[True]:
        ...

    @overload
    def __eq__(self, other: Any) -> Literal[False]:
        ...

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        return False


class DefaultValue(DEFAULT):
    def __new__(cls) -> Any:
        return super().__new__(cls)


FILL_SENTINEL = object()
VALUE_SENTINEL = object()
DEFAULT_OPTIONS = {"infinite_x": False, "infinite_y": False}
DEFAULT_VALUE = DEFAULT()


class Matrix:
    _coordinates: dict[tuple[int, int], Any]
    _options: dict[str, Any]
    rows: list[list[Any]]

    def __init__(
        self,
        rows: Matrix
        | list[str]
        | tuple[str, ...]
        | list[list[Any]]
        | tuple[list[Any], ...]
        | list[tuple[Any, ...]]
        | str
        | Values
        | None = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fill: Any = FILL_SENTINEL,
        *,
        options: Optional[dict[str, bool]] = None,
        infinite_x: bool | DEFAULT[Literal[True]] = DEFAULT_VALUE,
        infinite_y: bool | DEFAULT[Literal[True]] = DEFAULT_VALUE,
    ):
        if rows is None:
            rows = ()
        options_: dict[str, Any] = DEFAULT_OPTIONS.copy()
        if isinstance(rows, Matrix):
            input_matrix = rows
            rows = input_matrix.rows
            fill = input_matrix._fill if fill is FILL_SENTINEL else fill
            options_ = {**options_, **input_matrix._options}
        if isinstance(rows, Values):
            rows = rows.matrix.rows

        if options is not None:
            options_ = {**options_, **options}

        if infinite_x is not DEFAULT_VALUE:
            options_["infinite_x"] = bool(infinite_x)
        if infinite_y is not DEFAULT_VALUE:
            options_["infinite_y"] = bool(infinite_y)

        self._coordinates: dict[tuple[int, int], Any] = {}
        self.rows: list[str] | list[list[str]] | list[tuple[str, ...]] = (
            (
                list(cast(Iterable, rows))
                if isinstance(rows, (list, tuple, Iterable))
                else (str(rows).split("\n") if isinstance(rows, str) else rows)
            )
            if rows
            else []
        )
        self._options: dict[str, Any] = options_
        self._fill: Any = " " if fill is FILL_SENTINEL else fill

        while height is not None and height > len(self.rows):
            self.rows.append([])

        if width is not None:
            new_rows = []
            for row in self.rows:
                if isinstance(row, str) and width > len(row):
                    new_rows.append(row + (width - len(row)) * self._fill)
                elif isinstance(row, list) and width > len(row):
                    new_row = row + (width - len(row)) * [self._fill]
                    if isinstance(self._fill, str):
                        new_row = "".join(new_row)
                    new_rows.append(new_row)
                else:
                    new_rows.append(row)
            self.rows = new_rows

    def options(
        self,
        options: Optional[dict[str, Any]] = None,
        *,
        infinite_x: bool | DEFAULT[Literal[True]] = DEFAULT_VALUE,
        infinite_y: bool | DEFAULT[Literal[True]] = DEFAULT_VALUE,
    ) -> Matrix:
        return Matrix(self, options=options, infinite_x=infinite_x, infinite_y=infinite_y)

    @property
    def coordinates(self) -> dict[tuple[int, int], Any]:
        if self._coordinates:
            return self._coordinates
        for y, row in enumerate(self.rows):
            for x, c in enumerate(row):
                self._coordinates[(x, y)] = c
        return self._coordinates

    @property
    def width(self) -> int:
        return len(self.rows[0]) if self.rows else 0

    @property
    def height(self) -> int:
        return len(self.rows) if self.rows else 0

    @property
    def min_x(self) -> int:
        return 0 if self.rows else 0

    @property
    def min_y(self) -> int:
        return 0 if self.rows else 0

    @property
    def max_x(self) -> int:
        return (self.width - 1) if self.rows else 0

    @property
    def max_y(self) -> int:
        return (self.height - 1) if self.rows else 0

    def pad(
        self,
        size: Optional[int] = None,
        fill: Any = FILL_SENTINEL,
        left: Optional[int] = None,
        right: Optional[int] = None,
        top: Optional[int] = None,
        bottom: Optional[int] = None,
    ) -> Matrix:
        fill = self._fill if fill is FILL_SENTINEL else fill

        if size is not None:
            if (left or size) + (right or size) != size * 2:
                raise ValueError(f"invalid padding: {left} + {right} != {size * 2} (left + right != size * 2)")
            if (top or size) + (bottom or size) != size * 2:
                raise ValueError(f"invalid padding: {top} + {bottom} != {size * 2} (top + bottom != size * 2)")
            left = right = top = bottom = size
        if left is None and right is None and top is None and bottom is None:
            left = right = top = bottom = size = 1
        left = left or 0
        right = right or 0
        top = top or 0
        bottom = bottom or 0

        width = self.width + left + right

        rows = []
        if top is not None:
            rows += [fill * width] * top
        for row in self.rows:
            if not isinstance(fill, str) and isinstance(row, str):
                raise ValueError("invalid fill type: cannot pad a string row with a non-string fill")
            row_ = [fill] * left + list(row) + [fill] * right
            if isinstance(row, str):
                row_ = "".join(row_)
            rows.append(row_)
        if bottom is not None:
            rows += [fill * width] * bottom

        return Matrix(rows, fill=fill, options=self._options)

    def zoom(
        self,
        zoom: int = 2,
        fill: Any = FILL_SENTINEL,
        coordinates: Optional[
            set[tuple[int, int]] | list[tuple[int, int]] | tuple[tuple[int, int], ...] | dict[tuple[int, int], Any]
        ] = None,
    ) -> Matrix:
        if zoom < 1 and zoom == 0.5:
            return self.zoom_out()
        if zoom < 2:
            raise ValueError("zoom must be 2 or greater")
        fill = self._fill if fill is FILL_SENTINEL else fill
        matrix = Matrix(None, self.width * 2, self.height * 2, fill=fill)
        coordinates_ = self.coordinates if coordinates is None else coordinates
        if not isinstance(coordinates_, dict):
            coordinates_ = {pos: self[pos] for pos in coordinates_}
        for pos, char in coordinates_.items():
            pos_ = pos[0] * 2, pos[1] * 2
            matrix[(pos_[0], pos_[1])] = char
        return matrix

    def zoom_out(
        self,
    ) -> Matrix:
        matrix = Matrix(None, self.width // 2, self.height // 2, fill=self._fill)
        for pos, char in self.coordinates.items():
            if pos[0] % 2 != 0 or pos[1] % 2 != 0:
                continue
            pos_ = pos[0] // 2, pos[1] // 2
            matrix[(pos_[0], pos_[1])] = char
        return matrix

    def replace(self, old: Any, new: Any) -> Matrix:
        matrix = Matrix(self)
        for pos in self.position(old):
            matrix[pos] = new
        return matrix

    def count(self, value: Any) -> int:
        return len(self.position(value))

    def y(self, value: int, to_value: Optional[int] = None) -> Matrix | Any:
        if to_value is None:
            if len(self.rows[value]) > 1:
                return Matrix([self.rows[value]], fill=self._fill)
            return self.rows[value][0]
        return Matrix(self.rows[min(value, to_value) : (max(value, to_value) + 1)], fill=self._fill)

    def x(self, value: int, to_value: Optional[int] = None) -> Matrix | Any:
        if to_value is None:
            if len(self.rows) > 1:
                return Matrix([row[value] for row in self.rows], fill=self._fill)
            return self.rows[0][value]
        return Matrix([row[min(value, to_value) : (max(value, to_value) + 1)] for row in self.rows], fill=self._fill)

    def yx(self, y_value, x_value):
        return self.get(x_value, y_value)

    def xy(self, x_value, y_value):
        return self.get(x_value, y_value)

    def xyxy(self, x1, y1, x2, y2):
        return self.x(x1, x2).y(y1, y2)

    def xywh(self, x1, y1, w, h):
        x2 = x1 + w - 1
        y2 = y1 + h - 1
        return self.x(x1, x2).y(y1, y2)

    def yxhw(self, y1, x1, h, w):
        return self.xywh(x1, y1, w, h)

    def yxyx(self, y1, x1, y2, x2):
        return self.xyxy(x1, y1, x2, y2)

    def xy2xy(self, x1, y1, x2, y2):
        return self.xyxy(x1, y1, x2, y2)

    def yx2yx(self, y1, x1, y2, x2):
        return self.yxyx(y1, x1, y2, x2)

    def as_str(self) -> str:
        result = ""
        for row in self.rows:
            result += f"{row}\n"
        return result

    def __str__(self) -> str:
        return self.as_str()

    def draw(self) -> None:
        print(self.as_str())

    def print(self) -> None:
        print(self.as_str())

    def pos(self, char: Any, start_pos: Optional[tuple[int, int]] = None) -> list[tuple[int, int]]:
        x_index = 0 if start_pos is None else start_pos[0]
        positions = []
        for y, row in enumerate(self.rows):
            if start_pos is not None and start_pos[1] > y:
                continue
            if char not in row:
                continue
            try:
                index = x_index
                while True:
                    x = row.index(char, index)
                    positions.append((x, y))
                    index = x + len(char)
            except ValueError:
                pass

        return positions

    def pos_first(self, char: Any, start_pos: Optional[tuple[int, int]] = None) -> Optional[tuple[int, int]]:
        x_index = 0 if start_pos is None else start_pos[0]
        for y, row in enumerate(self.rows):
            if start_pos is not None and start_pos[1] > y:
                continue
            if char not in row:
                continue
            x = row.index(char, x_index)
            return (x, y)

        return None

    def pos_all(self, char, start_pos=None) -> list[tuple[int, int]]:
        return self.pos(char, start_pos)

    def pos_one(self, char, start_pos=None) -> Optional[tuple[int, int]]:
        return self.pos_first(char, start_pos)

    def pos_1(self, char, start_pos=None) -> Optional[tuple[int, int]]:
        return self.pos_first(char, start_pos)

    def position(self, char, start_pos=None) -> list[tuple[int, int]]:
        return self.pos(char, start_pos)

    def position_all(self, char, start_pos=None) -> list[tuple[int, int]]:
        return self.pos(char, start_pos)

    def position_first(self, char, start_pos=None) -> Optional[tuple[int, int]]:
        return self.pos_first(char, start_pos)

    def position_one(self, char, start_pos=None) -> Optional[tuple[int, int]]:
        return self.pos_first(char, start_pos)

    def position_1(self, char, start_pos=None) -> Optional[tuple[int, int]]:
        return self.pos_first(char, start_pos)

    def index(self, char, start_pos=None) -> Optional[tuple[int, int]]:
        return self.pos_first(char, start_pos)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, item, value):
        return self.set(item, value)

    @property
    def flip(self) -> Matrix:
        rows = []
        for x in range(0, self.max_x + 1):
            row = ""
            for y in range(0, self.max_y + 1):
                char = self.coordinates[(x, y)]
                row = f"{row}{char}"
            rows.append(row)
        return Matrix(rows, fill=self._fill)

    def rotate_right(self) -> Matrix:
        return Matrix(rows=[str(self.x(i)).replace("\n", "")[::-1].strip() for i in range(self.width)])

    def rotate_left(self) -> Matrix:
        return Matrix(rows=[str(self.x(i)).replace("\n", "").strip() for i in range(self.width - 1, -1, -1)])

    def mirror(self) -> Matrix:
        return Matrix(rows=[str(self.y(i)).replace("\n", "").strip() for i in range(self.height - 1, -1, -1)])

    def get(self, *args: Any, x: Any = None, y: Any = None) -> Any:
        if x is not None and y is not None and not args:
            args = (x, y)
        if isinstance(args, dict) and "x" in args and "y" in args:
            args = (args.get("x"), args.get("y"))
        if (
            len(args) == 1
            and isinstance(args[0], (tuple, list))
            and len(args[0]) == 2
            and isinstance(args[0][0], int)
            and isinstance(args[0][1], int)
        ):
            (args,) = args
        elif (
            len(args) == 1
            and isinstance(args[0], (tuple, list))
            and isinstance(args[0][0], (tuple, list))
            and len(args[0][0]) == 2
            and isinstance(args[0][0][0], int)
            and isinstance(args[0][0][1], int)
        ):
            return [self.get(p) for p in args[0]]

        x_, y_ = cast(tuple[int, int], args)

        while self._options.get("infinite_x") and x_ > self.max_x:
            x_ -= self.width
        while self._options.get("infinite_y") and y_ > self.max_y:
            y_ -= self.height

        try:
            return self.coordinates[x_, y_]
        except KeyError as exc:
            raise IndexError from exc

    def set(self, *args: Any, value: Any = VALUE_SENTINEL, x: Any = None, y: Any = None) -> None:
        if x is not None and y is not None and not args:
            args = (x, y)
        if isinstance(args, dict) and "x" in args and "y" in args:
            args = (args.get("x"), args.get("y"))
        if (
            len(args) == 1
            and isinstance(args[0], (tuple, list))
            and len(args[0]) == 2
            and isinstance(args[0][0], int)
            and isinstance(args[0][1], int)
        ):
            (args,) = args

        x_: int = 0
        y_: int = 0
        if (
            value is VALUE_SENTINEL
            and isinstance(args, (tuple, list))
            and len(args) == 2
            and isinstance(args[0], dict)
            and "x" in args[0]
            and "y" in args[0]
        ):
            args, value = args
            args = (args.get("x"), args.get("y"))
            x_, y_ = args
        elif (
            value is VALUE_SENTINEL
            and isinstance(args, (tuple, list))
            and len(args) == 3
            and isinstance(args[0], int)
            and isinstance(args[1], int)
        ):
            x_, y_, value = args
            args = x_, y_
        elif (
            value is VALUE_SENTINEL
            and isinstance(args, (tuple, list))
            and len(args) == 1
            and isinstance(args[0], (tuple, list))
            and len(args[0]) == 3
            and isinstance(args[0][0], int)
            and isinstance(args[0][1], int)
        ):
            (args,) = args
            x_, y_, value = args
            args = x_, y_
        elif (
            value is VALUE_SENTINEL
            and len(args) == 2
            and isinstance(args[0], (tuple, list))
            and len(args[0]) == 2
            and isinstance(args[0][0], int)
            and isinstance(args[0][1], int)
        ):
            args, value = args
            x_, y_ = args
        elif value is VALUE_SENTINEL:
            x_, y_ = args
        else:
            x_, y_, value = args

        while self._options.get("infinite_x") and x_ > self.max_x:
            x_ -= self.width
        while self._options.get("infinite_y") and y_ > self.max_y:
            y_ -= self.height

        try:
            self.coordinates[x_, y_] = value
            if isinstance(self.rows[y_], str):
                self.rows[y_] = self.rows[y_][0:x_] + value + self.rows[y_][(x_ + 1) :]
            else:
                self.rows[y_][x_] = value
        except KeyError as exc:
            raise IndexError from exc

    def __getattr__(self, item):
        item = item.replace("_", "-")
        m = re.match(r"^y([0-9-]+)x([0-9-]+)$", item)
        if m:
            y = int(m.group(1))
            x = int(m.group(2))
            return self.coordinates[x, y]
        m = re.match(r"^x([0-9-]+)y([0-9-]+)$", item)
        if m:
            x = int(m.group(1))
            y = int(m.group(2))
            return self.coordinates[x, y]
        m = re.match(r"^y([0-9-]+)$", item)
        if m:
            y = int(m.group(1))
            return self.rows[y]
        m = re.match(r"^x([0-9-]+)$", item)
        if m:
            x = int(m.group(1))
            return self.flip.rows[x]


from values import Values  # noqa: E402
