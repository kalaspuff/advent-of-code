import heapq

from helpers import tuple_add
from values import values


async def run() -> int:
    start = values.matrix.pos("S")[0]
    end = values.matrix.pos("E")[0]
    valid_positions = set(values.matrix.pos(".")) | {start, end}

    initial_direction = (1, 0)

    queue = [(0, start, initial_direction)]
    dist = {}
    dist[(start, initial_direction)] = 0
    predecessors = {}

    while queue:
        cost, pos, direction = heapq.heappop(queue)

        if pos == end:
            result = cost
            break

        next_pos = tuple_add(pos, direction)
        next_cost = cost + 1

        if next_pos in valid_positions:
            if (next_pos, direction) not in dist or next_cost < dist[(next_pos, direction)]:
                dist[(next_pos, direction)] = next_cost
                predecessors[(next_pos, direction)] = [(pos, direction)]
                heapq.heappush(queue, (next_cost, next_pos, direction))
            elif next_pos in valid_positions and next_cost == dist.get((next_pos, direction), float("inf")):
                predecessors[(next_pos, direction)].append((pos, direction))

        for new_dir in [
            (-direction[1], direction[0]),
            (direction[1], -direction[0]),
        ]:
            rotate_cost = cost + 1000
            if (pos, new_dir) not in dist or rotate_cost < dist[(pos, new_dir)]:
                dist[(pos, new_dir)] = rotate_cost
                predecessors[(pos, new_dir)] = [(pos, direction)]
                heapq.heappush(queue, (rotate_cost, pos, new_dir))
            elif rotate_cost == dist.get((pos, new_dir), float("inf")):
                predecessors[(pos, new_dir)].append((pos, direction))

    best_states = set()
    stack = [(end, d) for d in [(1, 0), (0, 1), (-1, 0), (0, -1)] if dist.get((end, d), float("inf")) == result]

    while stack:
        s = stack.pop()

        if s in best_states:
            continue

        best_states.add(s)

        for prev_s in predecessors.get(s, []):
            if prev_s not in best_states:
                stack.append(prev_s)

    best_positions = {pos for (pos, _) in best_states}
    return len(best_positions)


# [values.year]            (number)  2024
# [values.day]             (number)  16
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day16/input
#
# Result: 492
