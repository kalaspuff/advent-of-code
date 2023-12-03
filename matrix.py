import re
from typing import Any

FILL_SENTINEL = object()
VALUE_SENTINEL = object()


class Matrix:
    _coordinates = None
    _options = None
    _empty = None
    rows = None

    def __init__(self, rows, width=None, height=None, fill=FILL_SENTINEL, *, infinite_x=None, infinite_y=None):
        if isinstance(rows, Matrix):
            input_matrix = rows
            rows = input_matrix.rows
            fill = input_matrix._fill if fill is FILL_SENTINEL else fill
            infinite_x = infinite_x if infinite_x is not None else bool("infinite_x" in input_matrix._options)
            infinite_y = infinite_y if infinite_y is not None else bool("infinite_y" in input_matrix._options)

        self._coordinates = {}
        self.rows = (rows if isinstance(rows, (list, tuple)) else rows.split("\n")) if rows else []
        self._options = set()
        self._fill = " " if fill is FILL_SENTINEL else fill

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

        if infinite_x:
            self._options.add("infinite_x")
        if infinite_y:
            self._options.add("infinite_y")

    def options(self, infinite_x=None, infinite_y=None):
        infinite_x = infinite_x if infinite_x is not None else bool("infinite_x" in self._options)
        infinite_y = infinite_y if infinite_y is not None else bool("infinite_y" in self._options)
        return Matrix(self, infinite_x=infinite_x, infinite_y=infinite_y)

    @property
    def coordinates(self) -> dict[tuple[int, int], Any]:
        if self._coordinates:
            return self._coordinates
        for y, row in enumerate(self.rows):
            for x, c in enumerate(row):
                self._coordinates[(x, y)] = c
        return self._coordinates

    @property
    def width(self):
        return len(self.rows[0]) if self.rows else 0

    @property
    def height(self):
        return len(self.rows) if self.rows else 0

    @property
    def min_x(self):
        return 0 if self.rows else False

    @property
    def min_y(self):
        return 0 if self.rows else False

    @property
    def max_x(self):
        return (self.width - 1) if self.rows else False

    @property
    def max_y(self):
        return (self.height - 1) if self.rows else False

    def y(self, value, to_value=None):
        if to_value is None:
            if len(self.rows[value]) > 1:
                return Matrix([self.rows[value]], fill=self._fill)
            return self.rows[value][0]
        return Matrix(self.rows[min(value, to_value) : (max(value, to_value) + 1)], fill=self._fill)

    def x(self, value, to_value=None):
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

    def as_str(self):
        result = ""
        for row in self.rows:
            result += f"{row}\n"
        return result

    def __str__(self):
        return self.as_str()

    def draw(self):
        print(self.as_str())

    def print(self):
        print(self.as_str())

    def pos(self, char, start_pos=None):
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

    def pos_first(self, char, start_pos=None):
        x_index = 0 if start_pos is None else start_pos[0]
        for y, row in enumerate(self.rows):
            if start_pos is not None and start_pos[1] > y:
                continue
            if char not in row:
                continue
            x = row.index(char, x_index)
            return (x, y)

        return False

    def pos_all(self, char, start_pos=None):
        return self.pos(char, start_pos)

    def pos_one(self, char, start_pos=None):
        return self.pos_first(char, start_pos)

    def pos_1(self, char, start_pos=None):
        return self.pos_first(char, start_pos)

    def position(self, char, start_pos=None):
        return self.pos(char, start_pos)

    def position_all(self, char, start_pos=None):
        return self.pos(char, start_pos)

    def position_first(self, char, start_pos=None):
        return self.pos_first(char, start_pos)

    def position_one(self, char, start_pos=None):
        return self.pos_first(char, start_pos)

    def position_1(self, char, start_pos=None):
        return self.pos_first(char, start_pos)

    def index(self, char, start_pos=None):
        return self.pos_first(char, start_pos)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, item, value):
        return self.set(item, value)

    @property
    def flip(self):
        rows = []
        for x in range(0, self.max_x + 1):
            row = ""
            for y in range(0, self.max_y + 1):
                char = self.coordinates[(x, y)]
                row = f"{row}{char}"
            rows.append(row)
        return Matrix(rows, fill=self._fill)

    def get(self, *args, x=None, y=None):
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

        x_, y_ = args

        while "infinite_x" in self._options and x_ > self.max_x:
            x_ -= self.width
        while "infinite_y" in self._options and y_ > self.max_y:
            y_ -= self.height

        try:
            return self.coordinates[x_, y_]
        except KeyError:
            raise IndexError

    def set(self, *args, value=VALUE_SENTINEL, x=None, y=None):
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

        while "infinite_x" in self._options and x_ > self.max_x:
            x_ -= self.width
        while "infinite_y" in self._options and y_ > self.max_y:
            y_ -= self.height

        try:
            self.coordinates[x_, y_] = value
            if isinstance(self.rows[y_], str):
                self.rows[y_] = self.rows[y_][0:x_] + value + self.rows[y_][(x_ + 1) :]
            else:
                self.rows[y_][x_] = value
        except KeyError:
            raise IndexError

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
