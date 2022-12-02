import functools
import itertools
import math
import re

import helpers
from values import values


async def run():
    result = 0

    mapping = {
        "A": 1,
        "B": 2,
        "C": 3,
    }
    expect_mapping = {
        "X": "loss",
        "Y": "draw",
        "Z": "win",
    }
    res_mapping = {
        "win": 6,
        "draw": 3,
        "loss": 0,
    }

    for row in values.rows:
        they, expect = row.split(" ")
        game_result = expect_mapping[expect]

        me = ""
        if game_result == "draw":
            me = they
        elif game_result == "win":
            me = {"A": "B", "B": "C", "C": "A"}[they]
        elif game_result == "loss":
            me = {"A": "C", "B": "A", "C": "B"}[they]

        result += mapping[me]
        result += res_mapping[game_result]

    return result


# [values.year]            (number)  2022
# [values.day]             (number)  2
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day2/input
#
# Result: 11998
