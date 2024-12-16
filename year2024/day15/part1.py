from helpers import tuple_add
from matrix import Matrix
from values import values


async def run() -> int:
    result = 0

    warehouse_map, instruction_rows = values.split_sections("\n\n")
    warehouse = Matrix(warehouse_map)
    instructions = instruction_rows.flatten()

    walls = set(warehouse.pos("#"))
    robot = warehouse.pos("@")[0]
    boxes = set(warehouse.pos("O"))

    for instruction in instructions:
        direction: tuple[int, int]
        if instruction == "v":
            direction = (0, 1)
        elif instruction == "^":
            direction = (0, -1)
        elif instruction == ">":
            direction = (1, 0)
        elif instruction == "<":
            direction = (-1, 0)
        else:
            raise Exception(f"Invalid instruction: {instruction}")

        pos = tuple_add(robot, direction)

        if pos in walls:
            continue

        if pos not in boxes:
            robot = pos
            continue

        boxes_to_move = set()
        check_pos = pos
        while check_pos in boxes:
            boxes_to_move.add(check_pos)
            check_pos = tuple_add(check_pos, direction)

        if check_pos not in walls and check_pos not in boxes:
            boxes = (boxes - boxes_to_move) | {tuple_add(box_pos, direction) for box_pos in boxes_to_move}
            robot = pos

    for x, y in boxes:
        result += x + y * 100

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  15
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day15/input
#
# Result: 1538871
