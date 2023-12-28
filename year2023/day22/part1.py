import itertools

from helpers import Range
from values import values


class Brick:
    def __init__(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, *, id_: int | None = None):  # noqa: PLR0913
        self.x = Range(start=min(x1, x2), end=max(x1, x2))
        self.y = Range(start=min(y1, y2), end=max(y1, y2))
        self.z = Range(start=min(z1, z2), end=max(z1, z2))
        self.id_ = id_ if id_ is not None else 0xFFF

    def __repr__(self) -> str:
        return (
            f"Brick({self.id} · {self.x.start},{self.y.start},{self.z.start} ~ {self.x.end},{self.y.end},{self.z.end})"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Brick) and self.id_ == other.id_

    @property
    def id(self) -> str:
        return "0x" + "0" * (3 - len(hex(self.id_)[2:])) + hex(self.id_)[2:]

    def is_supported_by(self, other: "Brick") -> bool:
        return bool(min(self.z) - 1 == max(other.z) and self.x & other.x and self.y & other.y)

    def supports(self, other: "Brick") -> bool:
        return other.is_supported_by(self)

    @property
    def height_position(self):
        return min(self.z)

    def copy(self) -> "Brick":
        return Brick(self.x.start, self.y.start, self.z.start, self.x.end, self.y.end, self.z.end, id_=self.id_)


def simulate_fall(bricks: list[Brick]) -> list[Brick]:
    """
    Revised function to simulate the fall of the bricks, ensuring correct handling of the bricks' positions.
    """
    bricks = [b.copy() for b in bricks]
    bricks.sort(key=lambda brick: brick.height_position, reverse=False)
    occupied_positions: set[tuple[int, int, int]] = set()

    for brick in bricks:
        z = brick.height_position

        while z > 1 and not set(itertools.product(brick.x, brick.y, [z - 1])) & occupied_positions:
            z -= 1

        brick.z = brick.z + (z - brick.height_position)
        occupied_positions |= set(itertools.product(brick.x, brick.y, brick.z))

    return bricks


def simulate_removal(bricks: list[Brick]) -> int:
    removable_bricks = []

    for i, brick in enumerate(bricks):
        supporting = [b for b in bricks if b != brick and brick.supports(b)]
        if not supporting:
            removable_bricks.append(brick)
            continue

        scenario_without_brick = bricks[:i] + bricks[i + 1 :]
        scenario_without_brick.sort(key=lambda brick: brick.height_position, reverse=False)
        fallen_after_removal = simulate_fall(scenario_without_brick)

        if all(b.z == b_.z for b, b_ in zip(scenario_without_brick, fallen_after_removal)):
            removable_bricks.append(brick)

    return len(removable_bricks)


def print_brick_dependencies(bricks: list[Brick]) -> None:
    for brick in bricks:
        supporting = [b for b in bricks if b != brick and brick.supports(b)]
        supported_by = [b for b in bricks if b != brick and brick.is_supported_by(b)]

        print(f"{brick}:")
        print(f"  supporting: {supporting}")
        print(f"  supported by: {supported_by}")


async def run() -> int:
    bricks: list[Brick] = []
    for i, coordinates in enumerate(values):
        points = coordinates.split("~")
        x1, y1, z1 = map(int, points[0].split(","))
        x2, y2, z2 = map(int, points[1].split(","))
        bricks.append(Brick(x1, y1, z1, x2, y2, z2, id_=i))

    fallen_bricks = simulate_fall(bricks)
    print_brick_dependencies(fallen_bricks)
    return simulate_removal(fallen_bricks)


# [values.year]            (number)  2023
# [values.day]             (number)  22
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day22/input
#
# Result: 451
