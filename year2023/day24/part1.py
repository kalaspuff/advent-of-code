import itertools

from values import values


class Hailstone:
    def __init__(self, x: int, y: int, z: int, vx: int, vy: int, vz: int) -> None:  # noqa: PLR0913
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz

    @property
    def slope(self) -> float:
        # slope equation: "slope = rise / run" ::: ("vy" is "rise", "vx" is "run")
        # slope = vy / vx
        return self.vy / self.vx if self.vx != 0 else float("inf")

    @property
    def y_intercept(self) -> float:
        # slope-intersect form equation: "y = m * x + b" ::: ("slope" is "m", "b" is "y-intercept")
        # y_intercept = y - slope * x
        return self.y - self.slope * self.x if self.vx != 0 else float("inf")

    def at_time(self, t: int) -> "Hailstone":
        return Hailstone(
            x=self.x + self.vx * t,
            y=self.y + self.vy * t,
            z=self.z + self.vz * t,
            vx=self.vx,
            vy=self.vy,
            vz=self.vz,
        )

    def intersects_at(self, other: "Hailstone") -> tuple[float, float, float, float] | None:
        if self.slope == other.slope and self.y_intercept == other.y_intercept:
            # coinciding lines with an infinitude of points in common (all points on either of them)
            return float("inf"), float("inf"), float("inf"), float("inf")

        if self.slope == other.slope:
            # distinct but with same slope - parallel lines have no common points and never intersect
            return None

        # coordinates of intersection
        intersection_x = (other.y_intercept - self.y_intercept) / (self.slope - other.slope)
        intersection_y = self.slope * intersection_x + self.y_intercept

        # time until (or time since) intersection point for self (negative if a past intersection)
        intersection_time = (intersection_x - self.x) / self.vx

        # time until (or time since) intersection point for other (negative if a past intersection)
        other_intersection_time = (intersection_x - other.x) / other.vx

        return (intersection_x, intersection_y, intersection_time, other_intersection_time)

    def __repr__(self) -> str:
        return f"hailstone[x={self.x}, y={self.y}, z={self.z} | vx={self.vx}, vy={self.vy}, vz={self.vz}]"


async def run():
    hailstones = [Hailstone(*row.ints()) for row in values]

    test_area = (200000000000000, 400000000000000)
    if values.input_basename == "example":
        test_area = (7, 27)

    result = 0

    for h1, h2 in itertools.combinations(hailstones, 2):
        if intersection := h1.intersects_at(h2):
            x, y, t1, t2 = intersection
            if test_area[0] <= x <= test_area[1] and test_area[0] <= y <= test_area[1] and t1 >= 0 and t2 >= 0:
                result += 1

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  24
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day24/input
#
# Result: 18098 + 886858737029295
