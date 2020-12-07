from enum import Enum


class Opcode(Enum):
    ADD = 1
    MULTIPLY = 2
    STORE_INPUT = 3
    OUTPUT = 4
    JUMP_IF_TRUE = 5
    JUMP_IF_FALSE = 6
    LESS_THAN = 7
    EQUALS = 8
    HALT = 99
    UNKNOWN = -1

    @property
    def parameters(self):
        if self == Opcode.HALT or self == Opcode.UNKNOWN:
            return 0
        if self == Opcode.STORE_INPUT or self == Opcode.OUTPUT:
            return 1
        if self == Opcode.JUMP_IF_TRUE or self == Opcode.JUMP_IF_FALSE:
            return 2
        return 3


class IntcodeComputer:
    __slots__ = ("program", "state", "memory", "instruction_pointer", "operations_processed", "output", "output_function", "input_", "processing")

    def __init__(self, program):
        self.state = "INITIALIZING"
        self.output_function = None

        if isinstance(program, str):
            program = list(map(int, program.split(",")))
        elif isinstance(program, list):
            program = list(map(int, program))
        elif program and hasattr(program, "input_") and getattr(program, "input_", None):
            program = getattr(program, "input_", None)

        if isinstance(program, str):
            program = list(map(int, program.split(",")))
        elif isinstance(program, list):
            program = list(map(int, program))

        self.program = program
        self.reset()

    def input(self, input_):
        self.input_ = int(input_)

    def reset(self):
        self.memory = self.program[:]
        self.instruction_pointer = 0
        self.operations_processed = 0
        self.state = "INITIALIZED"
        self.input_ = None
        self.output = []
        self.processing = False

    @property
    def opcode(self):
        value = self.memory[self.instruction_pointer]
        if value >= 100:
            value = value % 100
        try:
            return Opcode(value)
        except Exception:
            return Opcode(-1)

    @property
    def instruction(self):
        parameters = self.opcode.parameters
        return self.memory[self.instruction_pointer:(self.instruction_pointer + 1 + parameters)]

    @property
    def parameter_modes(self):
        value = self.memory[self.instruction_pointer]
        mode_value = value // 100
        modes = list(map(int, list(f"{mode_value:03d}")))
        modes.reverse()
        return modes

    def process_instruction(self):
        self.processing = True
        instruction = self.instruction
        parameter_modes = self.parameter_modes
        instruction_pointer_before = self.instruction_pointer

        def read(p):
            return self.read(instruction[p], parameter_modes[p - 1])

        def store(p, value):
            return self.store(instruction[p], value)

        if self.opcode == Opcode.ADD:
            store(3, read(1) + read(2))
        elif self.opcode == Opcode.MULTIPLY:
            store(3, read(1) * read(2))
        elif self.opcode == Opcode.STORE_INPUT:
            store(1, self.input_)
        elif self.opcode == Opcode.OUTPUT:
            value = read(1)
            self.output.append(value)
            if self.output_function:
                self.output_function(value)
        elif self.opcode == Opcode.JUMP_IF_TRUE:
            if read(1):
                self.instruction_pointer = read(2)
        elif self.opcode == Opcode.JUMP_IF_FALSE:
            if not read(1):
                self.instruction_pointer = read(2)
        elif self.opcode == Opcode.LESS_THAN:
            if read(1) < read(2):
                store(3, 1)
            else:
                store(3, 0)
        elif self.opcode == Opcode.EQUALS:
            if read(1) == read(2):
                store(3, 1)
            else:
                store(3, 0)
        elif self.opcode == Opcode.HALT:
            self.state = "HALTING"
            self.operations_processed += 1
            self.processing = False
            return
        elif self.opcode == Opcode.UNKNOWN:
            self.state = "ERROR"
            self.processing = False
            return

        self.operations_processed += 1
        if self.instruction_pointer == instruction_pointer_before:
            self.instruction_pointer += len(instruction)
        self.processing = False

    def read(self, position, parameter_mode):
        if parameter_mode == 0:
            return self.memory[position]
        else:
            return position

    def store(self, position, value):
        self.memory[position] = value

    def run(self, input_=None, step=False):
        if input_ is not None:
            self.input(input_)
        self.state = "STARTING"

        def _run():
            self.state = "RUNNING"

            while self.state == "RUNNING":
                self.process_instruction()

                if self.state == "HALTING":
                    self.state = "FINISHED"
                    continue

                yield

            if self.state == "STOPPING":
                self.state = "STOPPED"

            yield

        machine = _run()
        if step:
            return machine

        try:
            while True:
                next(machine)
        except StopIteration:
            pass

    def stop(self):
        if self.state in ("RUNNING", "STARTING"):
            self.state = "STOPPING"

    def __str__(self):
        if self.state == "FINISHED" and self.opcode == Opcode.HALT:
            return f"<IntcodeComputer state=\"{self.state}\" ops={self.operations_processed} pointer={self.instruction_pointer}>"
        if self.processing:
            return f"<IntcodeComputer state=\"{self.state}\" ops={self.operations_processed} pointer={self.instruction_pointer} current={self.opcode}>"
        return f"<IntcodeComputer state=\"{self.state}\" ops={self.operations_processed} pointer={self.instruction_pointer} next={self.opcode}>"

    def __repr__(self):
        return str(self)
