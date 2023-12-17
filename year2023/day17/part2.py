import random

from helpers import tuple_add
from values import values

MIN_SINGLE_DIRECTION = 4
MAX_SINGLE_DIRECTION = 10


async def run() -> int:
    matrix = values.matrix
    queue: list[
        tuple[
            tuple[int, int],
            tuple[int, int],
            int,
            frozenset[tuple[int, int] | tuple[tuple[int, int], tuple[int, int]]],
            int,
        ]
    ] = [
        ((0, 0), (1, 0), 0, frozenset({}), 0),
        ((0, 0), (0, 1), 0, frozenset({}), 0),
    ]
    memo: dict[tuple[tuple[int, int], tuple[int, int], int], int] = {}
    min_heat_loss = float("inf")

    while queue:
        pos, direction, single_direction_count, visited_nodes, heat_loss = queue.pop(random.choice(range(len(queue))))

        if heat_loss >= min_heat_loss:
            continue

        key = (pos, direction, single_direction_count)
        if key in memo and memo.get(key, 0) < heat_loss:
            continue

        if pos == (matrix.width - 1, matrix.height - 1) and single_direction_count >= MIN_SINGLE_DIRECTION:
            min_heat_loss = min(min_heat_loss, heat_loss)
            print("current min_heat_loss:", min_heat_loss)
            queue = list(filter(lambda x: x[4] < min_heat_loss, queue))
            continue

        visited_nodes_ = (
            frozenset(visited_nodes | {(pos, direction)})
            if 1 <= single_direction_count < MIN_SINGLE_DIRECTION
            else frozenset(visited_nodes | {pos})
        )

        possible_directions: set[tuple[int, int]] = {(-1, 0), (0, -1), (1, 0), (0, 1)} - {
            (direction[0] * -1, direction[1] * -1)
        }
        if single_direction_count < MIN_SINGLE_DIRECTION:
            possible_directions = {direction}
        if single_direction_count == MAX_SINGLE_DIRECTION:
            possible_directions -= {direction}

        for direction_ in possible_directions:
            pos_ = tuple_add(pos, direction_)
            if pos_[0] < 0 or pos_[0] >= matrix.width or pos_[1] < 0 or pos_[1] >= matrix.height:
                continue

            single_direction_count_ = 1 if direction != direction_ else single_direction_count + 1

            if (single_direction_count_ >= MIN_SINGLE_DIRECTION and pos_ in visited_nodes_) or (
                single_direction_count_ < MIN_SINGLE_DIRECTION and (pos_, direction) in visited_nodes_
            ):
                continue

            heat_loss_ = heat_loss + int(str(matrix[pos_]))
            if heat_loss_ >= min_heat_loss:
                continue

            key_ = (pos_, direction_, single_direction_count_)
            if key_ in memo and memo.get(key_, 0) <= heat_loss_:
                continue
            memo[key_] = heat_loss_

            if single_direction_count_ >= MIN_SINGLE_DIRECTION and single_direction_count_ < MAX_SINGLE_DIRECTION:
                for i in range(single_direction_count_ + 1, MAX_SINGLE_DIRECTION + 1):
                    key_ = (pos_, direction_, i)
                    if key_ not in memo or memo.get(key_, 0) > heat_loss_:
                        memo[key_] = heat_loss_

            queue.append((pos_, direction_, single_direction_count_, visited_nodes_, heat_loss_))

    return int(min_heat_loss)


# [values.year]            (number)  2023
# [values.day]             (number)  17
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day17/input
#
# Result: 748
