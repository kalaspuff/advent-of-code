from values import values


class PulseType(type):
    pass


class LOW(metaclass=PulseType):
    pass


class HIGH(metaclass=PulseType):
    pass


class Pulse:
    def __init__(self, type_: PulseType, destination: "Module", sender: "Module | None" = None) -> None:
        self.type = type_
        self.destination = destination
        self.sender = sender

    def __repr__(self) -> str:
        if self.sender is None:
            return f'Pulse(type={self.type.__name__}, destination="{self.destination.name}")'
        return f'Pulse(type={self.type.__name__}, destination="{self.destination.name}", sender="{self.sender.name}")'


class Module:
    name: str
    _destinations: list[str]
    _inputs: list[str]

    _network: dict[str, "Module"]
    _pulse_queue: list[Pulse]

    def __new__(cls, name: str):
        self = super().__new__(cls)

        self.name = name
        self._destinations = cls._network[name]._destinations if name in cls._network else []
        self._inputs = cls._network[name]._inputs if name in cls._network else []

        cls._network[name] = self

        return self

    @classmethod
    def _update_config(cls, network: dict[str, "Module"], pulse_queue: list[Pulse]) -> None:
        cls._network = network
        cls._pulse_queue = pulse_queue

    def add_destination(self, destination: "Module | str"):
        if isinstance(destination, str):
            destination = self._network[destination] if destination in self._network else Module(destination)

        destination.add_input(self)
        if destination.name not in self._destinations:
            self._destinations.append(destination.name)

    def add_destinations(self, destinations: list["Module"] | list[str]):
        for destination in destinations:
            self.add_destination(destination)

    def add_input(self, input_: "Module | str") -> None:
        if isinstance(input_, str):
            input_ = self._network[input_] if input_ in self._network else Module(input_)

        if input_.name not in self._inputs:
            self._inputs.append(input_.name)

    @property
    def destinations(self) -> list["Module"]:
        return [self._network[destination] for destination in self._destinations]

    @property
    def inputs(self) -> list["Module"]:
        return [self._network[dest] for dest in self._inputs]

    @property
    def pulse_type(self) -> PulseType:
        return LOW

    def receive_pulse(self, pulse: Pulse) -> None:
        pass

    def send_pulse(self) -> None:
        for destination in self.destinations:
            self._send_pulse(destination)

    def trigger_pulse(self) -> None:
        self._send_pulse(self)

    def _create_pulse(self, destination: "Module") -> Pulse:
        return Pulse(self.pulse_type, destination=destination, sender=self)

    def _send_pulse(self, destination: "Module"):
        if isinstance(destination, str):
            destination = self._network[destination]
        self._pulse_queue.append(self._create_pulse(destination))

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name="{self.name}")'


class FlipFlopModule(Module):
    def __init__(self, name: str) -> None:
        self._state = False

    @property
    def pulse_type(self) -> PulseType:
        return HIGH if self._state else LOW

    def receive_pulse(self, pulse: Pulse) -> None:
        if pulse.type != LOW:
            return
        self._state = not self._state
        self.send_pulse()


class ConjunctionModule(Module):
    def __init__(self, name: str) -> None:
        self._state: dict[Module, PulseType] = {}

    @property
    def pulse_type(self) -> PulseType:
        return LOW if all(self._state.get(input_, LOW) == HIGH for input_ in self.inputs) else HIGH

    def receive_pulse(self, pulse: Pulse) -> None:
        if pulse.sender:
            self._state[pulse.sender] = pulse.type
        self.send_pulse()


class BroadcastModule(Module):
    def receive_pulse(self, pulse: Pulse) -> None:
        self.send_pulse()


async def run() -> int:
    network: dict[str, "Module"] = {}
    pulse_queue: list[Pulse] = []
    Module._update_config(network, pulse_queue)

    broadcaster = BroadcastModule("broadcaster")

    for module_char, (name, *destinations) in zip([row[0] for row in values], values.alphanums()):
        match module_char:
            case "%":
                FlipFlopModule(name).add_destinations(destinations)
            case "&":
                ConjunctionModule(name).add_destinations(destinations)
            case "b" if name == "broadcaster":
                broadcaster.add_destinations(destinations)
            case _:
                raise ValueError(f"invalid module char: {module_char}")

    pulse_count: dict[PulseType, int] = {HIGH: 0, LOW: 0}

    result = 0
    num_pushes = 0

    while not result:
        num_pushes += 1
        broadcaster.trigger_pulse()
        while pulse_queue:
            pulse = pulse_queue.pop(0)
            pulse_count[pulse.type] += 1

            destination = pulse.destination
            destination.receive_pulse(pulse)

        if num_pushes == 1000:
            result = pulse_count[HIGH] * pulse_count[LOW]

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  20
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day20/input
#
# Result: 856482136
