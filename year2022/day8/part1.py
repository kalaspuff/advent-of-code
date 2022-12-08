from values import values


async def run():
    matrix = values.matrix
    result = matrix.width * 2 + matrix.height * 2 - 4

    for y in range(1, matrix.height - 1):
        horizontal_row = list(map(int, matrix.y(y).rows[0]))
        for x in range(1, matrix.width - 1):
            value = horizontal_row[x]

            if all([value > v for v in horizontal_row[x + 1:]]) or all([value > v for v in horizontal_row[:x]]):
                result += 1
                continue

            vertical_row = list(map(int, matrix.x(x).flip.rows[0]))
            if all([value > v for v in vertical_row[y + 1:]]) or all([value > v for v in vertical_row[:y]]):
                result += 1
                continue

    return result


# [values.year]            (number)  2022
# [values.day]             (number)  8
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day8/input
#
# Result: 1779
