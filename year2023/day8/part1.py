from values import values


async def run() -> int:
    instructions = values[0]
    node_connections = {node: connections for node, *connections in values[2:].findall_alphanum()}

    current_node = "AAA"
    instruction_length = len(instructions)
    steps = 0

    while current_node != "ZZZ":
        direction = 0 if instructions[steps % instruction_length] == "L" else 1
        current_node = node_connections[current_node][direction]
        steps += 1

    return steps


# [values.year]            (number)  2023
# [values.day]             (number)  8
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day8/input
#
# Result: 17287
