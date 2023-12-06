import functools
import itertools
import math
import re
from collections import deque
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, TypeVar, Union

import helpers
from helpers import (
    inverse,
    inverse_dict,
    manhattan_distance,
    multisplit,
    transform,
    transform_dict,
    transform_tuple,
    tuple_add,
)
from matrix import Matrix
from values import values

if False:
    # potential copy-pasta / quick inspiration

    # > regex (full match + transform)
    # input: "Object 123: R 3 sX 8 9 | L a++ m nn X k"
    # output: (123, ["R", "3", "sX", "8", "9"], ["L", "a++", "m", "nn", "X", "k"])
    for object_id_, part_1_, part_2_ in values.match_rows(
        r"^[^\d]*(\d+):\s*(.*)\s*[|]\s*(.*)\s*$", transform=(int, str.split, str.split)
    ):
        pass

    # > regex (find all + transform)
    # input: "1  -  1, 48, 83, 86, 17; 83, 86,  6, 31, 17,  9, 48, 53"
    # output: (1, {1, 48, 17, 83, 86}, {6, 9, 48, 17, 83, 53, 86, 31})
    parse_numbers_ = lambda v_: set(map(int, v_.split(", ")))
    for single_, setpart_1_, setpart_2_ in values.findall_rows(
        r"((?:\d+(?:,\s+|)?)+)", transform=(int, parse_numbers_, parse_numbers_)
    ):
        pass

    # > multisplit
    # input: "a, b, c; d, e, f; g, h, i"
    # output: [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]
    result_ = multisplit(values.input, ["; ", ", "])

    # > inverse dict (flip key and value)
    # input: ["7 red", "3 green", "8 blue"]
    # output: {'red': 7, 'green': 3, 'blue': 8}
    result_ = inverse_dict(map(str.split, values.rows), transform=(str, int))

    # > add tuple elements (good for vectors, positions, coordinates)
    result_ = tuple_add((1, 2), (-1, 0))  # (0, 2)
    result_ = tuple_add((1, 2), (1, -1))  # (2, 1)

    # > get nearby vectors (positions) in a grid
    pos = (5, 6)
    for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
        pos_ = tuple_add(pos, mod)


async def run():
    result = 0

    for row in values.rows:
        pass

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  0
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day0/input
#
# Result: ...
