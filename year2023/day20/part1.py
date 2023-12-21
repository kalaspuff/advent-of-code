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
    _state: object
    _default_state: property

    def __new__(cls, name: str):
        self = super().__new__(cls)

        network = Network()

        self.name = name
        self._destinations = []
        self._inputs = []
        self._state = getattr(self, "_default_state", None)

        if name in network:
            self.add_destinations(network[name].destinations)
            self.add_inputs(network[name].inputs)

        network.add_module(self)

        return self

    def add_destination(self, destination: "Module | str") -> None:
        if isinstance(destination, str):
            network = Network()
            destination = network[destination] if destination in network else network.create_module(destination)

        destination.add_input(self)
        if destination.name not in self._destinations:
            self._destinations.append(destination.name)

    def add_destinations(self, destinations: list["Module"] | list[str]) -> None:
        for destination in destinations:
            self.add_destination(destination)

    def add_input(self, input_: "Module | str") -> None:
        if isinstance(input_, str):
            network = Network()
            input_ = network[input_] if input_ in network else network.create_module(input_)

        if input_.name not in self._inputs:
            self._inputs.append(input_.name)

    def add_inputs(self, inputs: list["Module"] | list[str]) -> None:
        for input_ in inputs:
            self.add_input(input_)

    @property
    def destinations(self) -> list["Module"]:
        network = Network()
        return [network[destination] for destination in self._destinations]

    @property
    def inputs(self) -> list["Module"]:
        network = Network()
        return [network[dest] for dest in self._inputs]

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
        Network().queue_pulse(self._create_pulse(destination))

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name="{self.name}")'


class FlipFlopModule(Module):
    _state: bool
    _default_state = property(lambda self: False)

    @property
    def pulse_type(self) -> PulseType:
        return HIGH if self._state else LOW

    def receive_pulse(self, pulse: Pulse) -> None:
        if pulse.type != LOW:
            return
        self._state = not self._state
        self.send_pulse()


class ConjunctionModule(Module):
    _state: dict[Module, PulseType]
    _default_state = property(lambda self: {})

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


class Network:
    _network: dict[str, Module]
    _queue: list[Pulse]
    _broadcaster: BroadcastModule
    _broadcast_count: int
    _pulse_count: dict[PulseType, int]

    def __new__(cls) -> "Network":
        try:
            if cls.__network is not None and cls.__network and cls.__network.fget:
                return cls.__network.fget(cls.__new__)
            return super().__new__(cls)
        except AttributeError:
            network = super().__new__(cls)
            network._network = {}
            network._queue = []
            network._broadcast_count = 0
            network._pulse_count = {LOW: 0, HIGH: 0}

            sentinel = cls.__new__

            def func(sentinel_):
                return network if sentinel_ is sentinel else None

            cls.__network = property(lambda *args: func(*args))
            return network

    def add_module(self, module: Module) -> Module:
        self._network[module.name] = module
        if isinstance(module, BroadcastModule) and module.name == "broadcaster":
            self._broadcaster = module
        return module

    def create_module(self, name: str) -> Module:
        module = Module(name)
        self._network[name] = module
        return module

    def queue_pulse(self, pulse: Pulse) -> None:
        self._queue.append(pulse)

    def broadcast_pulse(self, type_: PulseType = LOW) -> None:
        self._broadcast_count += 1
        self.queue_pulse(Pulse(type_, destination=self.broadcaster))

    @property
    def queue(self) -> list[Pulse]:
        return self._queue

    def next_pulse(self) -> Pulse | None:
        pulse = self._queue.pop(0) if self._queue else None
        if pulse:
            self._pulse_count[pulse.type] += 1
        return pulse

    def __getitem__(self, name: str) -> Module:
        if name not in self._network:
            raise KeyError(f"module {name} not found")
        return self._network[name]

    def __contains__(self, name: str) -> bool:
        return name in self._network

    @property
    def broadcaster(self) -> BroadcastModule:
        return self._broadcaster

    @property
    def broadcast_count(self) -> int:
        return self._broadcast_count

    @property
    def pulse_count(self) -> dict[PulseType, int]:
        return self._pulse_count


async def run() -> int:
    network = Network()

    for module_char, (name, *destinations) in zip([row[0] for row in values], values.alphanums()):
        match module_char:
            case "%":
                FlipFlopModule(name).add_destinations(destinations)
            case "&":
                ConjunctionModule(name).add_destinations(destinations)
            case "b" if name == "broadcaster":
                BroadcastModule(name).add_destinations(destinations)
            case _:
                raise ValueError(f"invalid module char: {module_char} (name: {name})")

    while network.broadcast_count < 1000:
        network.broadcast_pulse(LOW)
        while pulse := network.next_pulse():
            destination = pulse.destination
            destination.receive_pulse(pulse)

    return network.pulse_count[LOW] * network.pulse_count[HIGH]


# [values.year]            (number)  2023
# [values.day]             (number)  20
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day20/input
#
# Result: 856482136
