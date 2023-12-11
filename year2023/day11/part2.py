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
from values import Values, values

# https://docs.python.org/3/library/itertools.html
# https://docs.python.org/3/library/collections.html


async def run() -> int:
    result = 0

    for row in values.rows:
        pass

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  11
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day11/input
#
# Result: ...
