import math

from values import values


class PulseType(type):
    def __repr__(cls) -> str:
        return f"{cls.__name__}"


class LOW(metaclass=PulseType):
    pass


class HIGH(metaclass=PulseType):
    pass


class Pulse:
    def __init__(self, type_: PulseType, destination: "Module", sender: "Module | None" = None) -> None:
        self.type = type_
        self.destination = destination
        self.sender = sender
        self._status = "INIT"

    def process(self) -> None:
        self._status = "EXEC"
        try:
            self.destination.receive_pulse(self)
            self._status = "DONE"
        except Exception:
            self._status = "FAIL"
            raise

    def __repr__(self) -> str:
        sender_name = f'from: "{self.sender.name}"' if self.sender is not None else "<broadcast>"
        return f"[pulse: {str(self.type):4s} | {sender_name:21s} >> to: {str(self.destination):25s}    | <{self._status.lower():4s}> |::id:{hex(id(self))}::]"


class Module:
    name: str
    _destinations: list[str]
    _inputs: list[str]
    _network: "Network | None"
    _state: object
    _default_state: property

    def __new__(cls, name: str, *, network: "Network | None" = None, without_network: bool = False):
        self = super().__new__(cls)

        self.name = name
        self._destinations = []
        self._inputs = []
        self._network = None
        self._state = getattr(self, "_default_state", None)

        if not without_network:
            self.join_network(network if isinstance(network, Network) else Network())

        return self

    def add_destination(self, destination: "Module | str") -> None:
        if isinstance(destination, str):
            network = self._network
            if not network or (not network and destination not in self._destinations):
                self._destinations.append(destination)
                return
            destination = network[destination] if destination in network else network.create_module(destination)

        destination.add_input(self)
        if destination.name not in self._destinations:
            self._destinations.append(destination.name)

    def add_destinations(self, destinations: list["Module | str"] | list["Module"] | list[str]) -> None:
        for destination in destinations:
            self.add_destination(destination)

    def add_input(self, input_: "Module | str") -> None:
        if isinstance(input_, str):
            network = self._network
            if not network or (not network and input_ not in self._inputs):
                self._inputs.append(input_)
                return
            input_ = network[input_] if input_ in network else network.create_module(input_)

        if input_.name not in self._inputs:
            self._inputs.append(input_.name)

    def add_inputs(self, inputs: list["Module | str"] | list["Module"] | list[str]) -> None:
        for input_ in inputs:
            self.add_input(input_)

    @property
    def destinations(self) -> list["Module"]:
        if not self._network:
            raise ValueError("module not in network (use module._destinations instead)")
        return [self._network[destination] for destination in self._destinations]

    @property
    def inputs(self) -> list["Module"]:
        if not self._network:
            raise ValueError("module not in network (use module._inputs instead)")
        return [self._network[input_] for input_ in self._inputs]

    @property
    def pulse_type(self) -> PulseType:
        return LOW

    def receive_pulse(self, pulse: Pulse) -> None:
        pass

    def send_pulse(self) -> None:
        if not self._network:
            raise ValueError("cannot send pulse for module not in network")
        for destination in self.destinations:
            self._send_pulse(destination)

    def join_network(self, network: "Network | None" = None) -> None:
        if network is None:
            network = Network()

        destinations = network[self.name].destinations if self.name in network else []
        inputs = network[self.name].inputs if self.name in network else []

        self._network, _network = network, self._network
        try:
            network.add_module(self)
            self.add_destinations(destinations)
            self.add_inputs(inputs)
        except ValueError:
            self._network = _network
            raise

    def _create_pulse(self, destination: "Module") -> Pulse:
        return Pulse(self.pulse_type, destination=destination, sender=self)

    def _send_pulse(self, destination: "Module") -> Pulse:
        return self._queue_pulse(self._create_pulse(destination))

    def _broadcast_pulse(self, type_: PulseType | None = None) -> Pulse:
        if type_ is None:
            type_ = self.pulse_type
        return self._queue_pulse(Pulse(type_, destination=self))

    def _queue_pulse(self, pulse: Pulse) -> Pulse:
        if not self._network:
            raise ValueError("cannot send pulse for module not in network")
        self._network.queue_pulse(pulse)
        return pulse

    def __repr__(self) -> str:
        cls_name = type(self).__name__.lower().rstrip("module") or "module"
        return f'{cls_name}("{self.name}")'


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

    def __new__(cls, *, singleton: bool = True) -> "Network":
        try:
            if not singleton:
                raise AttributeError
            if cls.__network is not None and cls.__network and cls.__network.fget:
                return cls.__network.fget(cls.__new__)
            return super().__new__(cls)
        except AttributeError:
            network = super().__new__(cls)
            network._network = {}
            network._queue = []
            network._broadcast_count = 0
            network._pulse_count = {LOW: 0, HIGH: 0}

            if not singleton:
                return network

            sentinel = cls.__new__

            def func(sentinel_):
                return network if sentinel_ is sentinel else None

            cls.__network = property(lambda *args: func(*args))
            return network

    def add_module(self, module: Module) -> Module:
        name = module.name
        if name in self._network and type(self._network[name]) is not Module:
            raise ValueError(f'module "{name}" ({self._network[name]}) already exists')
        if module._network != self:
            module.join_network(self)
        else:
            self._network[name] = module
            if isinstance(module, BroadcastModule) and name == "broadcaster":
                self._broadcaster = module
        return module

    def create_module(
        self,
        name: str,
        destinations: list[Module | str] | list["Module"] | list[str] | None = None,
        module_cls: type[Module] = Module,
    ) -> Module:
        if name in self._network and type(self._network[name]) is not Module:
            raise ValueError(f'module "{name}" ({self._network[name]}) already exists')
        module = module_cls(name, network=self)
        if destinations:
            module.add_destinations(destinations)
        return module

    def queue_pulse(self, pulse: Pulse) -> None:
        self._queue.append(pulse)
        pulse._status = "WAIT"

    def broadcast_pulse(self, type_: PulseType = LOW) -> Pulse:
        self._broadcast_count += 1
        return self.broadcaster._broadcast_pulse(type_)

    @property
    def queue(self) -> list[Pulse]:
        return self._queue

    def next_pulse(self) -> Pulse | None:
        pulse = self._queue.pop(0) if self._queue else None
        if pulse:
            self._pulse_count[pulse.type] += 1
            pulse._status = "NEXT"
        return pulse

    def __getitem__(self, name: str) -> Module:
        if name not in self._network:
            raise KeyError(f"module {name} not found")
        return self._network[name]

    def __contains__(self, name: str) -> bool:
        return name in self._network

    def __repr__(self) -> str:
        return f"network({', '.join([f'{module}' for module in self._network.values()])})"

    def get(self, name: str, default: object = None) -> Module | object:
        return self._network.get(name, default)

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
                network.create_module(name, destinations, FlipFlopModule)
            case "&":
                network.create_module(name, destinations, ConjunctionModule)
            case "b" if name == "broadcaster":
                network.create_module(name, destinations, BroadcastModule)
            case _:
                raise ValueError(f"invalid module char: {module_char} (name: {name})")

    target = network["rx"]
    target_inputs: list[Module] = [input_ for module in target.inputs for input_ in module.inputs]
    target_values: dict[Module, int] = {}

    # debug output
    print("---")
    print(f'target: "{target.name}" ({target}) has {len(target.inputs)} input(s): {target._inputs}')
    for module in target.inputs:
        print(f'inputs: "{module.name}" ({module}) has {len(module.inputs)} input(s): {module._inputs}')
    if len(target.inputs) == 1:
        print("---")
        for input_ in target_inputs:
            print(f'expect: "{input_.name}" ({input_}) to send HIGH pulse to "{target.inputs[0].name}"')
    print("---")

    if len(target.inputs) != 1:
        raise ValueError(f"target has {len(target.inputs)} inputs, expected 1")
    if not isinstance(target.inputs[0], ConjunctionModule):
        raise TypeError(f"target input ({target.inputs[0]}) has invalid type, expected ConjunctionModule")

    while True:
        network.broadcast_pulse(LOW)
        while pulse := network.next_pulse():
            pulse.process()
            destination = pulse.destination

            if destination is target and pulse.type == LOW:
                # this is unlikely to happen with a reasonable amount of compute
                return network.broadcast_count

            if destination in target_inputs and destination.pulse_type == HIGH:
                name = destination.name
                count = network.broadcast_count
                if not [i for i in range(2, count) if count % i == 0] and all(
                    math.gcd(count, v) == 1 for v in target_values.values()
                ):
                    target_values[destination] = count

                # debug output
                print(f"[{name}] pulse is {destination.pulse_type.__name__} (count: {count})")
                print(f"[{name}] {len(target_values)} of {len(target_inputs)} values: {set(target_values.values())}")
                print(f"[{name}] current least common multiple: {math.lcm(*target_values.values())}")
                print("---")

                if len(target_values) == len(target_inputs):
                    return math.lcm(*target_values.values())


# [values.year]            (number)  2023
# [values.day]             (number)  20
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day20/input
#
# Result: 224046542165867
