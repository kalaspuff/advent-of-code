# `kalaspuff/advent-of-code`

*My solutions to some of the [Advent of Code](https://adventofcode.com/) programming puzzles.*

<img width="715" alt="aoc2022-computer-day7" src="https://user-images.githubusercontent.com/89139/207301060-74bdb4d2-c081-4a10-a38c-81ed8eaa79d1.png">

👆🧝💻 A custom shell for the device given by the Elves during [2022 - day 7](https://adventofcode.com/2022/day/7).

#### Writing solutions

Solutions go in the `yearYYYY/dayXX/part1.py` and `yearYYYY/dayXX/part2.py` files. The puzzle input goes into `yearYYYY/dayXX/input`. Additional example puzzle input could be put in the same folder with any arbitrary file name (`example` is a good name if there's only one type of example input).

The Python files `part1.py` and `part2.py` should have a function called `run` defined that will be called. The import `from values import values` is recommended to get easy access to the puzzle input.

Here's an example solution for the puzzle from year 2020, day 3, part 2.

```python
import math

from helpers import tuple_sum
from values import values


async def run():
    matrix = values.matrix.options(infinite_x=True)

    for move in [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]:
        chars = []
        pos = 0, 0

        try:
            while True:
                pos = tuple_sum(pos, move)
                chars.append(matrix[pos])
        except IndexError:
            pass

        values.result.append(chars.count("#"))

    return math.prod(values.result)
```


#### Running solutions

```
$ python aoc.py <year> <day> <part> [puzzle input filename]
```

If no puzzle input filename is specified, the default `input` file for the puzzle's day will be used as the puzzle input.

Example – to run the solution from the example above (year 2020, day 3, part 2).

```bash
$ python aoc.py 2020 3 2

# [values.year]            (number)  2020
# [values.day]             (number)  3
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2020/day3/input
# [values.result]          (list)    [63, 181, 55, 67, 30]
#
# Result: 1260601650
```
