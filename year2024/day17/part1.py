from values import values


async def run() -> str:
    registers = {"A": 0, "B": 0, "C": 0}
    for row in values:
        if row.startswith("Register"):
            reg, val = row.split(": ")
            registers[reg[-1]] = int(val)
        elif row.startswith("Program"):
            program = row.ints()

    opcode_instruction_mapping = {
        0: "adv",
        1: "bxl",
        2: "bst",
        3: "jnz",
        4: "bxc",
        5: "out",
        6: "bdv",
        7: "cdv",
    }

    def get_combo_value(op: int) -> int:
        if op <= 3:
            return op
        if op == 4:
            return registers["A"]
        if op == 5:
            return registers["B"]
        if op == 6:
            return registers["C"]
        return 0

    outputs = []
    instruction_pointer = 0
    while instruction_pointer < len(program):
        opcode = program[instruction_pointer]
        operand = program[instruction_pointer + 1]

        instruction = opcode_instruction_mapping[opcode]

        if instruction == "adv":
            registers["A"] //= 2 ** get_combo_value(operand)
        elif instruction == "bxl":
            registers["B"] ^= operand
        elif instruction == "bst":
            registers["B"] = get_combo_value(operand) % 8
        elif instruction == "jnz":
            if registers["A"] != 0:
                instruction_pointer = operand
                continue
        elif instruction == "bxc":
            registers["B"] ^= registers["C"]
        elif instruction == "out":
            outputs.append(get_combo_value(operand) % 8)
        elif instruction == "bdv":
            registers["B"] = registers["A"] // 2 ** get_combo_value(operand)
        elif instruction == "cdv":
            registers["C"] = registers["A"] // 2 ** get_combo_value(operand)

        instruction_pointer += 2

    return ",".join(map(str, outputs))


# [values.year]            (number)  2024
# [values.day]             (number)  17
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day17/input
#
# Result: 2,3,4,7,5,7,3,0,7
