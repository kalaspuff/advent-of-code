import heapq

from helpers import tuple_add
from values import values

# (x, y) - right, down, left, up
DIRECTIONS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))

# slope characters in the input (should be treated as ordinary trail paths)
SLOPE_CHARACTERS: tuple[str, ...] = (">", "v", "<", "^")


async def run() -> int:
    slopes: set[tuple[int, int]] = set()
    for char in SLOPE_CHARACTERS:
        slopes |= set(values.matrix.position(char))
    trail_path: set[tuple[int, int]] = set(values.matrix.position(".")) | slopes

    start_pos, end_pos = min(trail_path), max(trail_path)
    max_length = 0

    neighbors: dict[tuple[int, int], set[tuple[tuple[int, int], int, tuple[tuple[int, int], ...]]]] = {}

    # initial calculation of the valid neighbor positions (with length: 1) for each position on the trail paths
    for pos in trail_path:
        _neighbors: set[tuple[tuple[int, int], int, tuple[tuple[int, int], ...]]] = set()

        for mod in DIRECTIONS:
            pos_ = tuple_add(pos, mod)
            if pos_ not in trail_path:
                continue

            _neighbors.add((pos_, 1, (pos_,)))

        neighbors[pos] = _neighbors

    # optimizes neighbor mapping "recursively" for all positions with only two adjacent neighbors using merged lengths
    # a simple example: a->b->c | before: "a --(len 1)--> b --(len 1)--> c"                | after: "a -(len 2)-> c"
    # but also: a->b->c->d->... | before: "a --(len 1)--> b --(len 1)--> c --(len 1)--> d" | after: "a -(len 3)-> d"
    for pos in list(neighbors.keys()):
        if len(neighbors[pos]) != 2:
            continue

        subscriptable_ = list(neighbors[pos])
        for (pos_1, length_1, path_1), (pos_2, length_2, path_2) in zip(subscriptable_, subscriptable_[::-1]):
            search_path = (*path_1[::-1][1:], pos)
            new_path = (*search_path, *path_2)
            new_length = length_1 + length_2

            key = (neighbors[pos_1] & {(pos, length_1, search_path)}).pop()
            neighbors[pos_1].remove(key)
            neighbors[pos_1].add((pos_2, new_length, new_path))

        del neighbors[pos]

    def debug_trace_path(
        current_pos: tuple[int, int], visited: set[tuple[int, int]], path: tuple[tuple[int, int], ...]
    ) -> list[tuple[int, int]]:
        # traces the path from the start position to the current position using visited neighbors (ordered as path)
        detailed_path: list[tuple[int, int]] = [start_pos]
        visited_ = visited.copy() | {current_pos}
        path_ = path[:]

        pos = start_pos
        while pos != current_pos:
            indices = [
                (path_.index(pos_), pos_) for (pos_, _, _) in neighbors[pos] if pos_ in visited_ and pos_ in path_
            ]
            expect_pos = min(indices)[1]

            for pos_, _, detailed_path_ in neighbors[pos]:
                if pos_ != expect_pos:
                    continue
                if pos_ in visited_:
                    visited_.remove(pos)
                    pos = pos_
                    detailed_path.extend(detailed_path_)
                    break

        return detailed_path

    queue: list[tuple[int, int, tuple[int, int], set[tuple[int, int]]]] = []

    def enqueue(length: int, pos: tuple[int, int], visited: set[tuple[int, int]]) -> None:
        # a heap queue's first item is the item within it that compares with the lowest value
        # sort_key as _negative_ length so that the queue pops the _highest_ length item first
        sort_key = -length
        heapq.heappush(queue, (sort_key, length, pos, visited))

    enqueue(0, start_pos, {start_pos})

    found_path_count = 0
    while queue:
        _, length, pos, visited = heapq.heappop(queue)

        if pos == end_pos:
            # reached the end
            found_path_count += 1
            if max_length < length:
                print(f"current max length: {length} | number of full paths tested: {found_path_count}")

            max_length = max(max_length, length)
            continue

        for pos_, length_, _ in neighbors[pos]:
            if pos_ in visited:
                continue

            enqueue(length + length_, pos_, visited | {pos_})

    return max_length


# [values.year]            (number)  2023
# [values.day]             (number)  23
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day23/input
#
# Result:  6450
