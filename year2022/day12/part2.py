import string
import sys

from values import values


class Point:
    pos: tuple[int, int]
    _char: str
    _elevation: int
    _neighbours: tuple["Point", ...]
    _reversed_neighbours: tuple["Point", ...]
    _npos: tuple[tuple[int, int], ...]
    _distance: dict["Point", int]
    _paths: dict["Point", tuple["Point", ...]]

    _points: dict[tuple[int, int], "Point"]

    def __new__(cls, pos):
        if not getattr(cls, "_points", None):
            cls._points = {}
        pos = values.matrix.pos(pos)[0] if pos in ("S", "E") else pos
        if pos not in cls._points:
            value = super(cls, Point).__new__(cls)
            value.pos = pos
            cls._points[pos] = value
        return cls._points[pos]

    @property
    def char(self):
        if getattr(self, "_char", None) is not None:
            return self._char
        self._char = str(values.matrix[self.pos])
        return self._char

    @property
    def elevation(self):
        if getattr(self, "_elevation", None) is not None:
            return self._elevation
        if self.char == "S":
            return 0
        if self.char == "E":
            return 25
        self._elevation = string.ascii_lowercase.index(self.char)
        return self._elevation

    @property
    def neighbours(self):
        if getattr(self, "_neighbours", None) is not None:
            return self._neighbours

        _neighbours = []
        for np in self.npos:
            if self.elevation >= Point(np).elevation - 1:
                _neighbours.append(Point(np))

        self._neighbours = tuple(sorted(_neighbours, key=lambda p: (p.elevation, p.char == "E"), reverse=True))
        return self._neighbours

    @property
    def reversed_neighbours(self):
        if getattr(self, "_reversed_neighbours", None) is not None:
            return self._reversed_neighbours

        _neighbours = []
        for np in self.npos:
            if self.elevation <= Point(np).elevation + 1:
                _neighbours.append(Point(np))

        self._reversed_neighbours = tuple(
            sorted(_neighbours, key=lambda p: (p.elevation, p.char == "S"), reverse=False)
        )
        return self._reversed_neighbours

    @property
    def npos(self):
        if getattr(self, "_npos", None) is not None:
            return self._npos

        _npos = []
        x, y = self.pos
        for np in zip((x, x - 1, x, x + 1), (y - 1, y, y + 1, y)):
            if min(np) < 0 or np[0] >= values.matrix.width or np[1] >= values.matrix.height:
                continue
            _npos.append(np)

        self._npos = tuple(_npos)
        return self._npos

    def distance(self, target, point=None):
        if getattr(self, "_distance", None) is None:
            self._distance = {self: 0}

        if point is None:
            try:
                return self._distance[target] if target != self else 0
            except KeyError:
                self._distance[target] = sys.maxsize
                target.prepare(self)
                return self._distance[target]

        value = point.distance(target) + 1
        if target not in self._distance or self._distance[target] > value:
            self._distance[target] = min(self._distance.get(target, value), value)
            return True
        return False

    def prepare(self, target=None):
        path = [self]
        while path:
            point = path.pop()
            for p in point.neighbours:
                if p in path or p == self:
                    continue
                if p.distance(self, point):
                    if target and p == target:
                        break
                    path.append(p)

            path = sorted(path, key=lambda p: p.distance(self), reverse=True)

    def path(self, target):
        if getattr(self, "_paths", None) is None:
            self._paths = {}

        if target in self._paths:
            return self._paths[target]

        value = target.distance(self)
        result = (target,)
        for p in target.reversed_neighbours:
            if p.distance(self) > 0 and p.distance(self) == value - 1:
                result = (*self.path(p), target)
                break

        if not result or result[-1] != target or result[0] not in self.reversed_neighbours:
            return ()

        self._paths[target] = result
        return result

    def __repr__(self):
        return f"Point({self.pos[0]}, {self.pos[1]}, elevation={self.elevation})"


async def run():
    result = set()
    for start in values.matrix.pos("a") + ["S"]:
        path = Point(start).path(Point("E"))
        if path:
            result.add(len(path))

    return min(result)


# [values.year]            (number)  2022
# [values.day]             (number)  12
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day12/input
#
# Result: 522
