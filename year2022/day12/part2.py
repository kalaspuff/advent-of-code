import string

from values import values


async def run():
    matrix = values.matrix

    move = lambda pos, delta: tuple((v + d for v, d in (zip(pos, delta))))
    elevation = lambda c: string.ascii_lowercase.index("a" if c == "S" else ("z" if c == "E" else c))

    end = matrix.pos("E")[0]

    options = set()
    for start in matrix.pos("a") + [matrix.pos("S")[0]]:
        visited = set([start])
        lowest_visited = {start: 0}
        paths = set()

        path_stack = [(elevation(matrix[start]), 0, (start,))]

        while path_stack:
            best_values = max(path_stack)
            current_elevation, path_len, path = path_stack.pop(path_stack.index(best_values))
            current = path[-1]

            if not options and (not paths or max(paths)[0:2] < best_values[0:2]):
                print("BUILD", current_elevation, -path_len)

            if current == end:
                if not options or max(options)[0:2] < best_values[0:2]:
                    print("FOUND", current_elevation, -path_len)

                paths.add(best_values)
                continue

            for dir_delta in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                new_pos = move(current, dir_delta)

                if min(new_pos) < 0 or new_pos[0] >= matrix.width or new_pos[1] >= matrix.height:
                    continue

                if new_pos not in path:
                    new_elevation = elevation(matrix[new_pos])
                    new_path = (*path, new_pos)
                    new_path_len = len(new_path) - 1
                    if lowest_visited.get(new_pos, new_path_len + 1) > new_path_len and new_path not in visited and current_elevation >= new_elevation - 1:
                        path_stack.append((new_elevation, -new_path_len, new_path))
                        lowest_visited[new_pos] = new_path_len
                        visited.add(new_path)

        if paths:
            if not options or max(paths)[0:2] > max(options)[0:2]:
                print("ADDED", max(paths)[0], -max(paths)[1])
            options.add(max(paths))

    current_elevation, path_len, path = max(options)

    return -path_len


# [values.year]            (number)  2022
# [values.day]             (number)  12
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day12/input
#
# Result: 522
