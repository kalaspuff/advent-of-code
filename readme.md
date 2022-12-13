# `kalaspuff/advent-of-code`

*My solutions to some of the [Advent of Code](https://adventofcode.com/) programming puzzles.*

<img width="715" alt="aoc2022-computer-day7" src="https://user-images.githubusercontent.com/89139/207301060-74bdb4d2-c081-4a10-a38c-81ed8eaa79d1.png">

👆🧝💻 A custom shell for the device given by the Elves during [2022 - day 7](https://adventofcode.com/2022/day/7).

#### Writing solutions

Solutions go in the `yearYYYY/dayXX/part1.py` and `yearYYYY/dayXX/part2.py` files. The puzzle input goes into `yearYYYY/dayXX/input`. Additional example puzzle input could be put in the same folder with any arbitrary file name (`example` is a good name if there's only one type of example input).

The Python files `part1.py` and `part2.py` should have a function called `run` defined that will be called. The import `from values import values` is recommended to get easy access to the puzzle input.

Here's an example solution for the puzzle from [year 2020, day 3, part 2](https://adventofcode.com/2022/day/13).

```python
import functools
import operator
from typing import List

from values import values


def cmp(*args: List) -> int:
    return functools.reduce(
        lambda a, b: a or b,
        [
            cmp(*map(lambda v: [v, [v]][isinstance(v, int)], pair))
            if list in map(type, pair)
            else cmp(*map(lambda i: [[]] * i, pair))
            for pair in zip(*args)
        ]
        + [0],
    ) or max(min(1, operator.sub(*map(len, args))), -1)


async def run() -> int:
    divider1 = [[2]]
    divider2 = [[6]]

    rows = [eval(row) for row in values.rows if row] + [divider1, divider2]
    sorted_rows = [[]] + sorted(rows, key=functools.cmp_to_key(cmp))
    return (sorted_rows.index(divider1)) * (sorted_rows.index(divider2))


# [values.year]            (number)  2022
# [values.day]             (number)  13
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day13/input
#
# Result: 19570
```


#### Running solutions

```
$ python aoc.py <year> <day> <part> [puzzle input filename]
```

If no puzzle input filename is specified, the default `input` file for the puzzle's day will be used as the puzzle input.

Example – to run the solution from the example above (year 2022, day 13, part 2).

```bash
$ python aoc.py 2022 13 2

# [values.year]            (number)  2022
# [values.day]             (number)  13
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day13/input
# 
# Result: 19570
```
