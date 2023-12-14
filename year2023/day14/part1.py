from values import values


async def run() -> int:
    matrix = values.matrix

    for x in range(matrix.width):
        target_y: int | None = None
        for y in range(matrix.height):
            match matrix[(x, y)]:
                case "#":
                    target_y = None
                case "." if target_y is None:
                    target_y = y
                case "O" if target_y is not None:
                    matrix[(x, target_y)], matrix[(x, y)] = matrix[(x, y)], matrix[(x, target_y)]
                    target_y += 1

    return sum(matrix.height - y for _, y in matrix.position("O"))


# [values.year]            (number)  2023
# [values.day]             (number)  14
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day14/input
#
# Result: 105003
