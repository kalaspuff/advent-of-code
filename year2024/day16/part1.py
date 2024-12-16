from helpers import HeapQueue, tuple_add
from values import values


async def run() -> int:
    result = 0

    start = values.matrix.pos("S")[0]
    end = values.matrix.pos("E")[0]
    valid_positions = set(values.matrix.pos(".")) | {start, end}
    initial_direction = (1, 0)

    queue: HeapQueue[tuple[int, tuple[int, int], tuple[int, int]]] = HeapQueue((0, start, initial_direction))
    visited = set()

    while queue:
        cost, pos, direction = queue.pop()

        if pos == end:
            result = cost
            break

        key = (pos, direction)
        if key in visited:
            continue

        visited.add(key)

        next_pos = tuple_add(pos, direction)
        if next_pos in valid_positions:
            queue.append((cost + 1, next_pos, direction))

        for new_dir in [
            (-direction[1], direction[0]),
            (direction[1], -direction[0]),
        ]:
            queue.append((cost + 1000, pos, new_dir))

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  16
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day16/input
#
# Result: 85420
