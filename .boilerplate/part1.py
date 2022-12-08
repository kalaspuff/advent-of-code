import functools
import itertools
import math
import re

import helpers
from matrix import Matrix
from values import values
from year2022.computer import Command, Computer, Filesystem, Interface


async def run():
    result = 0

    # cpu = Computer("the device", filesystems=[Filesystem("root", mount="/", total_space=70000000)])
    # cpu.set_state_from_terminal_log(values.input_)
    # Interface(cpu).execute(Command("info"))
    # await Interface(cpu).connect()

    for row in values.rows:
        pass

    return result


# [values.year]            (number)  2022
# [values.day]             (number)  0
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day0/input
#
# Result: ...
