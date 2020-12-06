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
    taken_seat_ids = set()
    for row in values.rows:
        boardingpass = Boardingpass(row)
        taken_seat_ids.add(boardingpass.seat_id)

    return (set(range(min(taken_seat_ids), max(taken_seat_ids))) - taken_seat_ids).pop()


# [values.year]            (number)  2020
# [values.day]             (number)  5
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2020/day5/input
#
# Result: 565
