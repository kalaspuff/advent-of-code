from values import values


async def run():
    visited = set()
    head = tail = (0, 0)

    dir_delta = {
        "U": (0, -1),
        "R": (1, 0),
        "D": (0, 1),
        "L": (-1, 0),
    }

    move = lambda pos, delta: tuple((v + d for v, d in (zip(pos, delta))))

    for dir, count in values.match_rows(r"^([URDL]) ([0-9]+)$", (str, int)):
        for _ in range(count):
            head = move(head, dir_delta[dir])

            diff = tuple(h - t for h, t in zip(head, tail))
            if any((abs(v) > 1 for v in diff)):
                tail_delta = tuple(max(min(1, v), -1) for v in diff)
                tail = move(tail, tail_delta)

            visited.add(tail)

    return len(visited)


# [values.year]            (number)  2022
# [values.day]             (number)  9
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day9/input
#
# Result: 6212
