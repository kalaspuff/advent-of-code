import functools
import heapq
import itertools
import math
import re
from collections import Counter, deque
from functools import cache, lru_cache, reduce
from itertools import combinations, cycle, islice, permutations, product
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, TypeVar, Union

import helpers
from helpers import (
    Range,
    Ranges,
    batched,
    find_cyclic_pattern,
    find_layered_cyclic_pattern,
    inverse,
    inverse_dict,
    manhattan_distance,
    multisplit,
    paired,
    pairwise,
    position_ranges,
    sequence_delta_layers,
    sequence_delta_offset,
    sequence_offset_sum,
    transform,
    transform_dict,
    transform_tuple,
    tuple_add,
)
from matrix import Matrix
from values import Values, values

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

    # > Counter operations
    # input: "123ABC1232"
    # output: [('2', 3), ('1', 2), ('3', 2), ('A', 1), ('B', 1), ('C', 1)]
    Counter("123ABC1232").most_common()

    # > other useful methods
    values.findall_int()
    values.findall_alphanum()


# https://docs.python.org/3/library/itertools.html
# https://docs.python.org/3/library/collections.html


async def run() -> int:
    result = 0

    for row in values.rows:
        pass

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  0
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day0/input
#
# Result: ...
