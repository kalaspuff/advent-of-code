import math

from values import values


async def run() -> int:
    instructions = values[0]
    node_connections = {node: connections for node, *connections in values[2:].findall_alphanum()}

    starting_nodes = [node for node in node_connections if node.endswith("A")]
    instruction_length = len(instructions)
    cycle_lengths = {instruction_length}

    for starting_node in starting_nodes:
        current_node = starting_node
        steps = 0
        visited_nodes = {}
        while current_node not in visited_nodes:
            visited_nodes[current_node] = steps
            direction = 0 if instructions[steps % instruction_length] == "L" else 1
            current_node = node_connections[current_node][direction]
            steps += 1
        cycle_lengths.add(steps - visited_nodes[current_node])

    return math.prod(cycle_lengths)


# [values.year]            (number)  2023
# [values.day]             (number)  8
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day8/input
#
# Result: 18625484023687
