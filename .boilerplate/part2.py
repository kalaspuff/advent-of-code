import functools
import itertools
import math
import re
from collections import Counter, deque
from itertools import combinations, permutations, product
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, TypeVar, Union

import helpers
from helpers import (
    batched,
    inverse,
    inverse_dict,
    manhattan_distance,
    multisplit,
    paired,
    pairwise,
    position_ranges,
    transform,
    transform_dict,
    transform_tuple,
    tuple_add,
)
from matrix import Matrix
from values import Values, values

# https://docs.python.org/3/library/itertools.html
# https://docs.python.org/3/library/collections.html


async def run() -> int:
    result = 0

    for row in values.rows:
        pass

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  0
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day0/input
#
# Result: ...
