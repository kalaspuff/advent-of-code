from helpers import tuple_add
from matrix import Matrix
from values import values


def get_box_right(pos: tuple[int, int]) -> tuple[int, int]:
    return tuple_add(pos, (1, 0))


def get_box_left(pos: tuple[int, int]) -> tuple[int, int]:
    return tuple_add(pos, (-1, 0))


def get_box(pos: tuple[int, int], boxes: set[tuple[int, int]]) -> tuple[int, int] | None:
    if pos in boxes:
        return pos
    if get_box_left(pos) in boxes:
        return get_box_left(pos)
    return None


def try_move(
    box: tuple[int, int],
    direction: tuple[int, int],
    boxes: set[tuple[int, int]],
    walls: set[tuple[int, int]],
) -> bool:
    box_ = get_box(box, boxes)
    if box_ is None:
        return False

    box_right = get_box_right(box_)

    if tuple_add(box_, direction) in walls or tuple_add(box_right, direction) in walls:
        return False

    test_boxes = {
        get_box(tuple_add(box_, direction), boxes),
        get_box(tuple_add(box_right, direction), boxes),
    }

    for test_box in test_boxes:
        if not test_box or test_box == box_:
            continue
        if not try_move(test_box, direction, boxes, walls):
            return False

    boxes.remove(box_)
    boxes.add(tuple_add(box_, direction))

    return True


async def run() -> int:
    result = 0

    warehouse_map, instruction_rows = values.split_sections("\n\n")
    wide_warehouse_map = ""
    for row in warehouse_map:
        wide_warehouse_map += row.strip().replace("#", "##").replace(".", "..").replace("O", "[]").replace("@", "@.")

    warehouse = Matrix(wide_warehouse_map.strip())
    instructions = instruction_rows.flatten()

    walls = set(warehouse.pos("#"))
    robot = warehouse.pos("@")[0]
    boxes = set(warehouse.pos("["))

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

        box_positions = boxes | {get_box_right(box) for box in boxes}

        if pos not in box_positions:
            robot = pos
            continue

        original_boxes = boxes.copy()

        if try_move(pos, direction, boxes, walls):
            robot = pos
            continue
        else:
            boxes.clear()
            boxes.update(original_boxes)

    for x, y in boxes:
        result += x + y * 100

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  15
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day15/input
#
# Result: 1543338
