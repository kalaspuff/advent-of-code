from values import values


async def run() -> int:
    result = 0

    initial_registers = {"A": 0, "B": 0, "C": 0}
    for row in values:
        if row.startswith("Register"):
            reg, val = row.split(": ")
            initial_registers[reg[-1]] = int(val)
        elif row.startswith("Program"):
            initial_program = list(row.ints())

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

    # brute force

    start = 0
    incr = 1000000000

    start = 35184372088832  # 16 digit occurrence
    incr = 1000000000

    start = 190215511605248  # matches 3 last digits
    incr = 1000000

    start = 190352950558720  # matches 4 last digits
    incr = 100000

    start = 190378720362496  # matches 5 last digits
    incr = 100000

    start = 190384089071616  # matches 6 last digits
    incr = 100000

    start = 190384491724800  # matches 7 last digits
    incr = 1000

    start = 190384609165312  # matches 8 last digits
    incr = 1

    start = 190384609165312  # matches 9 last digits
    incr = 1

    start = 190384609427456  # matches 10 last digits
    incr = 1

    start = 190384609460224  # matches 11 last digits
    incr = 1

    start = 190384609460224  # matches 12 last digits
    incr = 1

    start = 190384609485312  # matches 13 last digits
    incr = 1

    start = 190384609508352  # matches 14 last digits
    incr = 1

    start = 190384609508360  # matches 15 last digits
    incr = 1

    start = 190384609508367  # matches all 16 digits
    incr = 1

    end = 283723065801743
    tries = 0

    for register_a in range(start, end, incr):
        tries += 1
        program = initial_program[:]
        registers = initial_registers.copy()
        registers["A"] = register_a

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

        if tries % 100000 == 0:
            print(register_a, len(outputs), outputs[3:])
        # if len(outputs) > 15:
        #     print(register_a, len(outputs))
        if outputs[4:] == initial_program[4:]:
            matches = 0
            for i, o in enumerate(reversed(outputs)):
                if o == initial_program[15 - i]:
                    matches += 1
                else:
                    break
            print(register_a, len(outputs), len(initial_program), matches, outputs, initial_program)
        if outputs == initial_program:
            result = register_a
            break

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  17
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day17/input
#
# Result: 190384609508367
