from helpers import binary_space_partitioning
from values import values


class Boardingpass:
    def __init__(self, value):
        self.value = value

    @property
    def row(self):
        return binary_space_partitioning(self.value[0:7], 0, 127, "F", "B")

    @property
    def column(self):
        return binary_space_partitioning(self.value[7:10], 0, 7, "L", "R")

    @property
    def seat_id(self):
        return self.row * 8 + self.column


async def run():
    seat_ids = set()
    for row in values.rows:
        boardingpass = Boardingpass(row)
        seat_ids.add(boardingpass.seat_id)

    return max(seat_ids)


# [values.year]            (number)  2020
# [values.day]             (number)  5
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2020/day5/input
#
# Result: 828
