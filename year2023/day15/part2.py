import functools

from values import values


class Box:
    def __init__(self):
        self.lenses = {}

    def add(self, label: str, focal_length: int | str) -> None:
        self.lenses[label] = int(focal_length)

    def remove(self, label: str) -> None:
        self.lenses.pop(label, None)

    @property
    def power(self) -> int:
        return sum(slot * focal_length for slot, focal_length in enumerate(self.lenses.values(), start=1))


async def run() -> int:
    boxes = [Box() for box in range(256)]

    for sequence in values.flatten().split(","):
        func, (*args,) = (Box.remove, (sequence[:-1],)) if "-" in sequence else (Box.add, sequence.split("="))
        label = args[0]

        index = functools.reduce(lambda current, char: (current + ord(char)) * 17 % 256, label, 0)
        box = boxes[index]

        func.__get__(box, None)(*args)

    return sum((index + 1) * box.power for index, box in enumerate(boxes))


# [values.year]            (number)  2023
# [values.day]             (number)  15
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day15/input
#
# Result: 236057
