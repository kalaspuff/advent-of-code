# note to self: need to clean this up A LOT. solved initially with networkx, but rewriting for fun.
# lots of temporary code and broken stuff at the moment.

import functools
import heapq
import itertools
import math
import random
import re
from collections import Counter, deque
from functools import cache, lru_cache, reduce
from itertools import combinations, cycle, islice, permutations, product
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    List,
    MutableSet,
    Optional,
    Self,
    Sequence,
    Set,
    Sized,
    Tuple,
    TypeVar,
    Union,
    dataclass_transform,
)

import helpers
import networkx
import networkx as nx
from helpers import (
    Range,
    Ranges,
    batched,
    find_cyclic_pattern,
    find_layered_cyclic_pattern,
    inverse,
    inverse_dict,
    manhattan_distance,
    multisplit,
    paired,
    pairwise,
    position_ranges,
    sequence_delta_layers,
    sequence_delta_offset,
    sequence_offset_sum,
    transform,
    transform_dict,
    transform_tuple,
    tuple_add,
)
from matrix import Matrix
from values import Values, values

NT = TypeVar("NT", bound=Hashable)
NC = TypeVar("NC", bound=Collection)
NN = TypeVar("NN", bound="Node")


class Node(Generic[NT, NC]):
    _id: NT
    _nodes: Collection[NT]
    _input_nodes: set[NT]
    _network: "Network[Node[NT, NC], NT, NC] | None"
    _storage: dict[str, Any]

    def __new__(cls, id_: NT, *, network: "Network | None" = None, without_network: bool = False):
        self = super().__new__(cls)

        self._id = id_
        self._nodes = set()
        self._input_nodes = set()
        self._network = None
        self._storage = {}

        if not without_network:
            self.join_network(network if isinstance(network, Network) else Network())

        return self

    def add_node(self, node: "Node[NT, NC] | NT") -> None:
        if not isinstance(node, Node):
            network = self._network
            if not network or (not network and node not in self._nodes):
                self._add_node(node)
                return
            node = network[node] if node in network else network.create_node(node)

        if node.name not in self._nodes:
            self._add_node(node.name)
        node._add_input_node(self)

    def _add_node(self, node: NT) -> None:
        if isinstance(self._nodes, set):
            self._nodes.add(node)
        elif isinstance(self._nodes, tuple):
            self._nodes = (*self._nodes, node)
        elif isinstance(self._nodes, frozenset):
            self._nodes = frozenset({*self._nodes, node})
        elif isinstance(self._nodes, list):
            self._nodes.append(node)
        elif getattr(self._nodes, "append", None):
            getattr(self._nodes, "append")(node)  # noqa: B009
        elif getattr(self._nodes, "add", None):
            getattr(self._nodes, "add")(node)  # noqa: B009
        else:
            raise TypeError(f"cannot add node to {type(self._nodes)}")

    def _remove_node(self, node: NT) -> None:
        if isinstance(self._nodes, (set, list)):
            self._nodes.remove(node)
        elif isinstance(self._nodes, tuple):
            self._nodes = tuple(node_ for node_ in self._nodes if node_ != node)
        elif isinstance(self._nodes, frozenset):
            self._nodes = frozenset({node_ for node_ in self._nodes if node_ != node})
        elif getattr(self._nodes, "remove", None):
            getattr(self._nodes, "remove")(node)  # noqa: B009
        else:
            raise TypeError(f"cannot remove node from {type(self._nodes)}")

    def _add_input_node(self, node: "Node[NT, NC]") -> None:
        self._input_nodes.add(node.name)
        self.add_input_node(node)

    def add_input_node(self, node: "Node[NT, NC]") -> None:
        # defaults to input nodes also being destination nodes
        if node.name not in self._nodes:
            self.add_node(node.name)

    def _remove_input_node(self, node: "Node[NT, NC]") -> None:
        if node.name in self._input_nodes:
            self._input_nodes.remove(node.name)

    def add_nodes(self, nodes: Collection["Node[NT, NC]"]) -> None:
        for node in nodes:
            self.add_node(node)

    @property
    def nodes(self) -> Collection["Node[NT, NC]"]:
        if not self._network:
            raise ValueError("node not in network (use node._nodes instead)")
        return {self._network[node] for node in self._nodes}

    @property
    def input_nodes(self) -> Collection["Node[NT, NC]"]:
        if not self._network:
            raise ValueError("node not in network (use node._input_nodes instead)")
        return {self._network[node] for node in self._input_nodes}

    @property
    def name(self) -> NT:
        return self._id

    def join_network(self, network: "Network | None" = None) -> None:
        if network is None:
            network = Network()

        nodes = network[self.name].nodes if self.name in network else []
        self._network, _network = network, self._network
        try:
            network.add_node(self)
            if nodes:
                self.add_nodes(nodes)
        except ValueError:
            self._network = _network
            raise

    def leave_network(self) -> None:
        if not self._network:
            raise ValueError("node not in network")
        network = self._network
        self._network = None
        network.remove_node(self)

    def disconnect_node(self, node: "Node[NT, NC] | NT") -> None:
        if not self._network:
            raise ValueError("node not in network")
        if isinstance(node, Node):
            node = node.name
        if node in self._nodes:
            self._remove_node(node)
            if self._network and node in self._network:
                other = self._network[node]
                other.disconnect_node(self)
                other._remove_input_node(self)

    def disconnect_all(self) -> None:
        for node in self._nodes:
            self.disconnect_node(node)

    def connect_node(self, node: "Node[NT, NC] | NT") -> None:
        if not self._network:
            raise ValueError("node not in network")
        if isinstance(node, Node):
            node = node.name
        if node not in self._nodes:
            self._add_node(node)
            if self._network and node in self._network:
                self._network[node].connect_node(self)

    def connect_all(self) -> None:
        for node in self._nodes:
            self.connect_node(node)

    def __repr__(self) -> str:
        basic_names = ("node", "module", "point", "edge", "component")
        cls_name = type(self).__name__.lower()
        for name in basic_names:
            if cls_name.endswith(name):
                cls_name = cls_name[: -len(name)]
            if not cls_name:
                break

        return f"N({self.name}·{cls_name}{len(self._nodes)})"

    def __gt__(self, other: "Node") -> int:
        return bool(self.name > other.name)

    def __lt__(self, other: "Node") -> int:
        return bool(self.name < other.name)

    def __ge__(self, other: "Node") -> int:
        return bool(self.name >= other.name)

    def __le__(self, other: "Node") -> int:
        return bool(self.name <= other.name)

    def __cmp__(self, other: "Node") -> int:
        return 1 if self.name > other.name else -1 if self.name < other.name else 0

    def __copy__(self) -> Self:
        node = type(self)(self.name, without_network=True)
        node._nodes = self._nodes
        node._network = self._network
        node._storage = self._storage
        return node

    def __hash__(self) -> int:
        return hash(("Node", self.name, id(self)))


class Network(Generic[NN, NT, NC]):
    name: str | None
    _nodes: dict[NT, NN]
    _partitions: tuple[frozenset[NN], ...]
    _should_recalculate_partitions: bool
    _flow: dict[
        tuple[NN | Node[NT, NC], NN | Node[NT, NC]],
        tuple[
            int,
            list[tuple[tuple[int, float, tuple[str, ...]], tuple[NN | Node[NT, NC], ...], float]],
            dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], int],
            dict[NN | Node[NT, NC], int],
        ],
    ]
    _distances: dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], tuple[int, tuple[NN | Node[NT, NC], ...]]]

    _default_singleton: bool = False
    _default_node_cls: type[NN] | type[Node[NT, NC]] | None = None

    def __new__(
        cls,
        *,
        name: str | None = None,
        nodes: Collection[NN] | None = None,
        singleton: bool | None = None,
    ) -> "Network":
        if singleton is None:
            singleton = cls._default_singleton
        try:
            if not singleton:
                raise AttributeError
            if cls.__network is not None and cls.__network and cls.__network.fget:
                if name is not None or nodes is not None:
                    raise ValueError("cannot supply name or nodes to an initiated singleton network")
                return cls.__network.fget(cls.__new__)
            return super().__new__(cls)
        except AttributeError:
            nodes_: dict[NT, NN] = {}
            network = super().__new__(cls)
            network.name = name
            network._nodes = nodes_
            network._partitions = ()
            network._flow = {}
            network._distances = {}
            network._should_recalculate_partitions = False

            if nodes:
                for node in nodes:
                    network.add_node(node)

            if not singleton:
                return network

            sentinel = cls.__new__

            def func(sentinel_):
                return network if sentinel_ is sentinel else None

            cls.__network = property(lambda *args: func(*args))
            return network

    def add_node(self, node: NN) -> NN:
        if not isinstance(node, Node):
            raise TypeError("node must be of Node instance, use network.create_node() to create nodes")

        name: NT = node.name
        if name in self._nodes and type(self._nodes[name]) is not Node:
            raise ValueError(f'node "{name}" ({self._nodes[name]}) already exists')

        if node._network != self:
            node.join_network(self)
        else:
            self._nodes[name] = node

        if node._nodes:
            self._should_recalculate_partitions = True
        return node

    def create_node(
        self,
        name: NT,
        nodes: Collection[NN] | None = None,
        node_cls: type[NN] | type[Node[NT, NC]] | None = None,
    ) -> Node:
        if node_cls is None:
            node_cls = self._default_node_cls if self._default_node_cls else Node[NT, NC]

        if name in self._nodes and type(self._nodes[name]) is not Node:
            raise ValueError(f'node "{name}" ({self._nodes[name]}) already exists')

        node: NN | Node[NT, NC] = node_cls(name, network=self)
        if nodes:
            node.add_nodes(nodes)
            self._should_recalculate_partitions = True
        return node

    def remove_node(self, node: Node | str) -> None:
        if isinstance(node, str):
            node = self[node]
        if node.name not in self._nodes:
            raise ValueError(f'node "{node.name}" not in network')

        node.disconnect_all()
        node.leave_network()
        self._nodes.pop(node.name, None)
        self._should_recalculate_partitions = True
        self._flow = {}
        self._distances = {}

    def disconnect(
        self, source: NN | Node[NT, NC] | NT, sink: NN | Node[NT, NC] | NT | Collection[NN | Node[NT, NC] | NT]
    ) -> None:
        if not isinstance(source, Node):
            source = self[source]
        if source.name not in self._nodes:
            raise ValueError(f'source node "{source.name}" not in network')

        if not isinstance(sink, Node) and (
            not isinstance(sink, Collection)
            or len(sink) > 0
            and (not isinstance(next(iter(sink)), Collection) or isinstance(next(iter(sink)), str))
        ):
            sink = self[sink]
        if isinstance(sink, Collection) and not isinstance(sink, str):
            for sink_ in sink:
                self.disconnect(source, sink_)
            return
        if not isinstance(sink, Node) or sink.name not in self._nodes:
            raise ValueError(f'sink node "{sink.name if isinstance(sink, Node) else str(sink)}" not in network')

        source.disconnect_node(sink)
        self._should_recalculate_partitions = True
        self._flow = {}
        self._distances = {}

    def connect(
        self, source: NN | Node[NT, NC] | NT, sink: NN | Node[NT, NC] | NT | Collection[NN | Node[NT, NC] | NT]
    ) -> None:
        if not isinstance(source, Node):
            source = self[source]
        if source.name not in self._nodes:
            raise ValueError(f'source node "{source.name}" not in network')

        if not isinstance(sink, Node) and (
            not isinstance(sink, Collection)
            or len(sink) > 0
            and (not isinstance(next(iter(sink)), Collection) or isinstance(next(iter(sink)), str))
        ):
            sink = self[sink]
        if isinstance(sink, Collection) and not isinstance(sink, str):
            for sink_ in sink:
                self.connect(source, sink_)
            return
        if not isinstance(sink, Node) or sink.name not in self._nodes:
            raise ValueError(f'sink node "{sink.name if isinstance(sink, Node) else str(sink)}" not in network')

        source.connect_node(sink)
        self._should_recalculate_partitions = True
        self._flow = {}
        self._distances = {}

    @property
    def nodes(self) -> Collection[NN]:
        return [self[name] for name, _ in self._nodes.items()]

    @property
    def size(self) -> int:
        return len(self)

    @property
    def length(self) -> int:
        return len(self)

    @property
    def partitions(self) -> tuple[frozenset[NN], ...]:
        # print("partitions:", self._should_recalculate_partitions)
        if self._should_recalculate_partitions:
            self._should_recalculate_partitions = False
            self._recalculate_partitions()
        return self._partitions

    @classmethod
    def get_partitions(cls, nodes: NC | Iterable[NN] | Sequence[NN] | set[NN]) -> tuple[frozenset[NN], ...]:
        partitions: list[set[NN]] = [set(nodes)]

        # initial_count = len(partitions[0])
        # print("partitions:", len(partitions))
        # node_union: set[NN] = {next(iter(partitions[0]))}
        # print("before:", len(node_union))
        # print("before:", len(partitions[0]))
        # processed_nodes: set[NN] = set()
        # while node_union - processed_nodes:
        #     node = next(iter(node_union - processed_nodes))
        #     processed_nodes.add(node)
        #     node_union |= set(node.nodes)
        # print("after:", len((node_union)))
        # if len(node_union) == initial_count:
        #    print("fixed")
        #    return tuple(sorted([frozenset(partition) for partition in partitions], key=len))

        class RecalculatePartitionsError(Exception):
            pass

        while True:
            try:
                partitions = [set(partition) for partition in partitions if partition]
                for partition in partitions:
                    if not partition:
                        partitions.remove(partition)
                        raise RecalculatePartitionsError

                    for node in partition:
                        for partition_ in partitions:
                            if partition_ is not partition and node in partition_:
                                partition_.remove(node)
                                raise RecalculatePartitionsError

                        for node_ in node.nodes:
                            if node_ is node or node_ == node:
                                raise Exception("node in node.nodes")
                            if node not in node_.nodes:
                                for partition_ in partitions:
                                    if node_ in partition_:
                                        partition_.remove(node_)
                                raise RecalculatePartitionsError

                            if node in node_.nodes and node_ not in partition:
                                partition.add(node_)
                                for partition_ in partitions:
                                    if partition_ is not partition and node_ in partition_:
                                        partition_.remove(node_)
                                raise RecalculatePartitionsError

                    node_union: set[NN] = {next(iter(partition))}
                    processed_nodes: set[NN] = set()
                    while node_union - processed_nodes:
                        node = next(iter(node_union - processed_nodes))
                        processed_nodes.add(node)
                        node_union |= set(node.nodes)

                    # print("node_union", len(node_union))
                    # print("partition", len(partition))

                    if node_union != partition:
                        if node_union & partition == partition and node_union & partition == node_union:
                            partitions.remove(partition)
                            if node_union in partitions:
                                partitions.remove(node_union)
                            partitions.append(partition | node_union)
                            raise RecalculatePartitionsError
                        if (node_union - partition) & (partition - node_union):
                            partitions.remove(partition)
                            if node_union in partitions:
                                partitions.remove(node_union)
                            partitions.append(partition ^ node_union)
                            partitions.append(partition & node_union)
                            raise RecalculatePartitionsError

                        partitions.remove(partition)
                        if node_union in partitions:
                            partitions.remove(node_union)
                        partitions.append(node_union)
                        partitions.append(partition - node_union)
                        raise RecalculatePartitionsError

            except RecalculatePartitionsError:
                continue

            break

        return tuple(sorted([frozenset(partition) for partition in partitions], key=len))

    def _recalculate_partitions(self) -> None:
        self._partitions = self.get_partitions(set(self._nodes.values()))

    def calculate_maximum_flow(
        self,
        source: NN | Node[NT, NC] | NT,
        sink: NN | Node[NT, NC] | NT,
        force_update: bool = False,
    ) -> int:
        maximum_flow, augmenting_paths, edge_capacity, node_capacity = self._calculate_flow(source, sink, force_update)
        return maximum_flow

    def find_augmenting_paths(
        self, source: NN | Node[NT, NC] | NT, sink: NN | Node[NT, NC] | NT
    ) -> dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], int]:
        maximum_flow, augmenting_paths, edge_capacity, node_capacity = self._calculate_flow(source, sink)
        return augmenting_paths

    def calculate_final_edge_capacity(
        self, source: NN | Node[NT, NC] | NT, sink: NN | Node[NT, NC] | NT
    ) -> dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], int]:
        maximum_flow, augmenting_paths, edge_capacity, node_capacity = self._calculate_flow(source, sink)
        return edge_capacity

    def calculate_final_node_capacity(
        self, source: NN | Node[NT, NC] | NT, sink: NN | Node[NT, NC] | NT
    ) -> dict[NN | Node[NT, NC], int]:
        maximum_flow, augmenting_paths, edge_capacity, node_capacity = self._calculate_flow(source, sink)
        return node_capacity

    def calculate_mincut(
        self, source: NN | Node[NT, NC] | NT, sink: NN | Node[NT, NC] | NT, expected_cut_value: int | None = None
    ) -> tuple[int, set[tuple[NN | Node[NT, NC], NN | Node[NT, NC]]], tuple[frozenset[NN], ...]]:
        if not isinstance(source, Node):
            source = self[source]
        if not isinstance(source, Node) or source.name not in self._nodes:
            raise ValueError(f'source node "{source.name}" not in network')

        if not isinstance(sink, Node):
            sink = self[sink]
        if not isinstance(sink, Node) or sink.name not in self._nodes:
            raise ValueError(f'sink node "{sink.name}" not in network')

        current_partitions = self.partitions[:]
        maximum_flow = self.calculate_maximum_flow(source, sink)
        if expected_cut_value is not None and maximum_flow < expected_cut_value:
            raise ValueError(
                f'maximum flow too low ({maximum_flow}, expected {expected_cut_value}) for source ("{source.name}") and sink ("{sink.name}") that partitions the network [0]'
            )

        partition = current_partitions[0]
        for partition_ in current_partitions:
            if source in partition_ and sink in partition_:
                partition = partition_

        print(f"calculate mincut ({source.name} -> {sink.name}): maximum flow: {maximum_flow} ({len(partition)} nodes)")

        cuts: set[tuple[NN | Node[NT, NC], NN | Node[NT, NC]]] = set()

        _distances = self._distances
        _flow = self._flow

        try:
            while True:
                if expected_cut_value and len(cuts) == expected_cut_value:
                    raise ValueError(
                        f'no cuts found for source ("{source.name}") and sink ("{sink.name}") that partitions the network [1]'
                    )

                edges = (*self.find_bottleneck_edges(source, sink).keys(), *tuple(self.edges))
                # print("FINAL CAPACITY", self.calculate_final_capacity(source, sink))
                # print(edges)

                # breakpoint()
                # print(edges)

                for edge in edges:
                    node, node_ = edge

                    if node not in partition or node_ not in partition:
                        # print("!!!!!!!! not in partition", node, node_)
                        continue

                    if node is sink or node is source or node_ is sink or node_ is source:
                        continue

                    self.disconnect(node, node_)
                    cuts.add(edge)

                    # self._should_recalculate_partitions = True
                    updated_partitions = self.partitions[:]

                    if len(updated_partitions) != len(current_partitions):
                        # print("BREAK BREAK", len(updated_partitions), len(current_partitions))
                        break

                    maximum_flow_ = self.calculate_maximum_flow(source, sink)
                    print(
                        f"len(cuts): {len(cuts)}, cuts: {cuts} | source: {source} -> {sink} | {node} -> {node_} | maximum_flow: {maximum_flow} -> {maximum_flow_}"
                    )

                    # print(f"edge: {edge} | maximum flow: {maximum_flow} -> {maximum_flow_}")
                    if maximum_flow_ < maximum_flow:
                        maximum_flow = maximum_flow_
                        # print("BREAK BREAK BREAAAAAK")
                        break

                    self.connect(node, node_)
                    cuts.remove(edge)
                else:
                    raise ValueError(
                        f'no cuts found for source ("{source.name}") and sink ("{sink.name}") that partitions the network [1]'
                    )

                if len(updated_partitions) != len(current_partitions):
                    break
        except ValueError as exc:
            print("calculate_mincut error:", str(exc))
            raise exc
        finally:
            for node, node_ in cuts:
                self.connect(node, node_)

            self._distances = _distances
            self._flow = _flow
            self._partitions = current_partitions

        print("success:", len(cuts), cuts, len(updated_partitions))
        return len(cuts), cuts, updated_partitions

    @property
    def edges(self) -> set[tuple[NN | Node[NT, NC], NN | Node[NT, NC]]]:
        result: set[tuple[NN | Node[NT, NC], NN | Node[NT, NC]]] = set()

        for node in self.nodes:
            for node_ in node.nodes:
                if node_ is node or node_ == node:
                    continue
                edge = self.get_edge((node, node_))
                result.add(edge)

        return result

    def get_edge(
        self,
        edge: tuple[NN | Node[NT, NC], NN | Node[NT, NC]] | NN | Node[NT, NC],
        _arg: NN | Node[NT, NC] | None = None,
    ) -> tuple[NN | Node[NT, NC], NN | Node[NT, NC]]:
        if isinstance(edge, tuple):
            node, node_ = edge
        else:
            node = edge
            node_ = _arg
        if not node or not node_:
            raise ValueError("invalid edge: requires two nodes")
        return (node_, node) if node_ < node and node in node_.nodes and node_ in node.nodes else (node, node_)

    def _calculate_flow(
        self,
        source: NN | Node[NT, NC] | NT,
        sink: NN | Node[NT, NC] | NT,
        force_update: bool = False,
    ) -> tuple[
        int,
        list[tuple[tuple[int, float, tuple[str, ...]], tuple[NN | Node[NT, NC], ...], float]],
        dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], int],
        dict[NN | Node[NT, NC], int],
    ]:
        if not isinstance(source, Node):
            source = self[source]
        if not isinstance(source, Node) or source.name not in self._nodes:
            raise ValueError(f'source node "{source.name}" not in network')

        if not isinstance(sink, Node):
            sink = self[sink]
        if not isinstance(sink, Node) or sink.name not in self._nodes:
            raise ValueError(f'sink node "{sink.name}" not in network')

        flow_key: tuple[NN | Node[NT, NC], NN | Node[NT, NC]] = (source, sink)

        if not force_update and self._flow and flow_key in self._flow:
            return self._flow[flow_key]

        queue: list | set = []  # e: list[tuple[int, NN | Node[NT, NC], set[NN | Node[NT, NC]], tuple[NN | Node[NT, NC], ...]]] = []

        def enqueue(
            queue: list | set,
            node: NN | Node[NT, NC],
            prev: NN | Node[NT, NC],
            visited: set[NN | Node[NT, NC]] | frozenset[NN | Node[NT, NC]],
            path: tuple[NN | Node[NT, NC], ...],
            # path: tuple[NN | Node[NT, NC], ...],
            # score: int,
        ) -> None:
            # a heap queue's first item is the item within it that compares with the lowest value
            # sort_key as _negative_ flow value so that the queue pops the edge with _highest_ flow first
            # sort_key = (
            #     # score,
            #     # -total_queued_count,
            #     -(
            #         flow.get((prev, node), 0)
            #         + flow.get((node, prev), 0)  # - len(visited) + random.randint(0, len(visited))
            #     ),
            #     -len(visited),
            # )
            # sort_key = -total_queued_count
            # if sort_key != 0:
            #    print((prev, node), sort_key)
            # print(flow.get((prev, node), 0))
            # print((prev, node), sort_key)

            sort_key = len(visited)
            entry_with_sort_key = (sort_key, node, prev, frozenset(visited), path)

            if isinstance(queue, set):
                queue.add(entry_with_sort_key)
            elif isinstance(queue, list):
                heapq.heappush(queue, entry_with_sort_key)
            else:
                raise TypeError(f"invalid queue type: {type(queue)}")

            # heapq.heappush(queue, (sort_key, node, prev, frozenset(visited)))

        def convert_queue(
            queue: list | set,
            type_: type[list] | type[set] | None = None,
        ) -> list | set:
            if isinstance(queue, set) and (type_ is list or type_ is None):
                queue = list(queue)
                heapq.heapify(queue)
            elif isinstance(queue, list) and (type_ is set or type_ is None):
                queue = set(queue)
            return queue

        def pop_queue(queue: list | set) -> tuple | None:
            if not queue or len(queue) == 0:
                return None
            entry: tuple
            if isinstance(queue, set):
                _, *entry = queue.pop()
            elif isinstance(queue, list):
                _, *entry = heapq.heappop(queue)
            else:
                raise TypeError(f"invalid queue type: {type(queue)}")

            return entry

        flow: dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], int] = {}
        total_queued_count: int = 0
        source_sink_max_distance = 0
        source_sink_min_distance = float("inf")

        maximum_flow = 0
        edge_capacity: dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], int] = {}
        augmenting_paths: list[tuple[tuple[int, float, tuple[str, ...]], tuple[NN | Node[NT, NC], ...], float]] = []
        flow_paths: list[tuple[tuple[NN | Node[NT, NC], ...], float]] = []
        # distances: dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], tuple[int, tuple]] = self._distances

        network_size = len(self._nodes)
        all_visited: set[NN | Node[NT, NC]] = set()
        all_visited_by_path: set[tuple[NN | Node[NT, NC], ...]] = set()

        for edge in self.edges:
            edge_capacity[edge] = 1
            flow[edge] = 0

        def sum_node_capacity(node) -> int:
            result: int = 0
            for node_ in node.nodes:
                if node is node_ or node == node_:
                    continue
                edge = self.get_edge(node, node_)
                result += edge_capacity[edge]
            return result

        # using "networkx" lib for now, as i don't have time to implement proper maximum flow and mincut algorithms.
        # todo: implement own proper flow function (more efficient than a naive shortest augmenting path dfs)
        _IMPLEMENTATION = "networkx"

        if _IMPLEMENTATION == "networkx":
            nxgraph = networkx.Graph()

            for node in self.nodes:
                for node_ in node.nodes:
                    if node is node_ or node == node_:
                        continue
                    edge = self.get_edge(node, node_)
                    nxgraph.add_edge(node, node_, capacity=edge_capacity[edge])

            # for edge, capacity in edge_capacity.items():
            #    nxgraph.add_edge(*edge, capacity=capacity)

            maximum_flow, flow_ = networkx.maximum_flow(
                nxgraph,
                source,
                sink,
            )

            for node, flow_info in flow_.items():
                for node_, flow_value in flow_info.items():
                    edge = self.get_edge(node, node_)
                    flow[edge] = flow_value

            for edge, flow_value in flow.items():
                edge_capacity[edge] -= flow_value

            node_capacity: dict[NN | Node[NT, NC], int] = {}
            for node in self.nodes:
                node_capacity[node] = sum_node_capacity(node)

            return_value = (
                maximum_flow,
                augmenting_paths,
                self._sort_dict_by_value(edge_capacity),
                self._sort_dict_by_value(node_capacity),
            )
            self._flow[flow_key] = return_value

            return return_value

        if _IMPLEMENTATION == "something-an-elf-could-have-built":
            # exerimental own code, dragon's, etc. (works somewhat, also slow)

            if False:
                # to use the queue as a set instead of as a sorted heapq
                queue = convert_queue(queue, set)

            enqueue(queue, source, source, {source}, (source,))

            # find shortest augmenting path
            while entry := pop_queue(queue):
                node, prev, visited, path = entry

                all_visited.add(node)

                if node is sink:
                    minimum_capacity = float("inf")
                    for i, (from_, to_) in enumerate(list(zip(path, path[1:]))):
                        edge = self.get_edge(from_, to_)
                        minimum_capacity = min(minimum_capacity, edge_capacity[edge])

                    if minimum_capacity > 0:
                        minimum_capacity = 0 if minimum_capacity == float("inf") else int(minimum_capacity)

                        if len(visited) < source_sink_min_distance:
                            print(
                                f"{source} -> {sink}: current best flow route: {minimum_capacity} capacity via {len(visited)} nodes (current queue: {len(queue)})"
                            )

                        source_sink_max_distance = max(source_sink_max_distance, len(visited))
                        source_sink_min_distance = min(source_sink_min_distance, len(visited))

                        sort_key = (len(visited), -minimum_capacity, tuple(str(p.name) for p in path))
                        path_data = (sort_key, path[:], minimum_capacity)
                        heapq.heappush(augmenting_paths, path_data)

                        # print(
                        #     f"{source} -> {sink}: visited through {len(visited)} nodes (min: {source_sink_min_distance} | max: {source_sink_max_distance}) :: capacity: {minimum_capacity} :: maximum flow: {maximum_flow} :: queue: {len(queue)}"
                        # )

                    continue

                if len(visited) <= source_sink_min_distance:
                    for node_ in node.nodes:
                        if node_ is not prev and node_ in visited and node in node_.nodes:
                            # non-optimal path: could've been reached through a shorter path
                            break
                    else:
                        minimum_capacity = float("inf")
                        for from_, to_ in zip(path, path[1:]):
                            edge = self.get_edge(from_, to_)
                            minimum_capacity = min(minimum_capacity, edge_capacity[edge])
                            if minimum_capacity <= 0:
                                break
                        else:
                            for node_ in node.nodes:
                                if node_ is prev or node_ is node or node_ == node:
                                    continue
                                if node_ in visited:
                                    continue

                                enqueue(queue, node_, node, visited | {node_}, (*path, node_))
                                total_queued_count += 1

                                if total_queued_count % 10000 == 0:
                                    print(
                                        f"* total queued: {total_queued_count} :: current queue: {len(queue)} :: visited nodes: {len(all_visited)} (of {len(self._nodes)}) :: path len: {len(visited)} ({len(path)})"
                                    )

                if not queue and augmenting_paths:
                    _, path, minimum_capacity = augmenting_paths[0]
                    minimum_capacity = int(minimum_capacity)
                    maximum_flow += minimum_capacity

                    print(
                        f"{source} -> {sink}: adding flow to augmenting path of length {len(path)} :: capacity: {minimum_capacity} (current maximum flow: {maximum_flow})"
                    )

                    for from_, to_ in zip(path, path[1:]):
                        edge = self.get_edge(from_, to_)
                        edge_capacity[edge] -= minimum_capacity
                        flow[edge] = flow.get(edge, 0) + minimum_capacity

                    flow_paths.append((path, minimum_capacity))

                    source_sink_max_distance = 0
                    source_sink_min_distance = float("inf")
                    augmenting_paths = []
                    enqueue(queue, source, source, {source}, (source,))

            node_capacity: dict[NN | Node[NT, NC], int] = {}
            for node in self.nodes:
                node_capacity[node] = sum_node_capacity(node)

            return_value = (
                maximum_flow,
                augmenting_paths,
                self._sort_dict_by_value(edge_capacity),
                self._sort_dict_by_value(node_capacity),
            )
            self._flow[flow_key] = return_value

            return return_value

        return

    def _sort_dict_by_value(self, dict_: dict, *, reverse: bool = False) -> dict:
        return {v_: k_ for k_, v_ in sorted([(v, k) for k, v in dict_.items()], reverse=reverse)}

    def find_mincut(
        self, expected_cut_value: int | None = None, expected_partition_increase: int | None = None
    ) -> tuple[int, set[tuple[NN | Node[NT, NC], NN | Node[NT, NC]]], tuple[frozenset[NN], ...]]:
        node_combination_count = len(self) * len(self)
        bad_choices: set[tuple[NN, NN]] = set()
        cuts: set[tuple[NN | Node[NT, NC], NN | Node[NT, NC]]] = set()
        tries = 0

        current_partitions = self.partitions[:]

        while node_combination_count > len(bad_choices):
            randomized_source = random.choice(list(self._nodes.values()))
            randomized_sink = random.choice(list(self._nodes.values()))

            if randomized_source == randomized_sink:
                bad_choices.add((randomized_source, randomized_sink))

            if (randomized_source, randomized_sink) in bad_choices:
                continue

            tries += 1
            bad_choices.add((randomized_source, randomized_sink))
            bad_choices.add((randomized_sink, randomized_source))

            maximum_flow = self.calculate_maximum_flow(randomized_source, randomized_sink, force_update=True)

            if expected_cut_value is not None and maximum_flow != expected_cut_value:
                print(
                    f"{randomized_source} -> {randomized_sink}: residual network has maximum flow: {maximum_flow} (need {expected_cut_value} -- retrying)"
                )
                continue

            print(
                f"{randomized_source} -> {randomized_sink}: using residual network with {maximum_flow} maximum flow (success)"
            )

            edge_capacity = self.calculate_final_edge_capacity(randomized_source, randomized_sink)
            # print(edge_capacity)

            nxgraph = networkx.Graph()

            for node in self.nodes:
                for node_ in node.nodes:
                    if node is node_ or node == node_:
                        continue
                    edge = self.get_edge(node, node_)
                    nxgraph.add_edge(node, node_, capacity=edge_capacity[edge])

            cut_value, partition = networkx.minimum_cut(nxgraph, randomized_source, randomized_sink)
            print(cut_value, len(partition))
            print(partition)
            breakpoint()

            # for edge, capacity in edge_capacity.items():
            #     nxgraph.add_edge(*edge, capacity=capacity)

            # cut_value = 100
            # while cut_value > 3:
            #     k1 = random.choice(list(graph.edges.keys()))[0]
            #     k2 = random.choice(list(graph.edges.keys()))[0]
            #
            #     # bfs from k1 to k2
            # cut_value, partition = networkx.minimum_cut(graph, k1, k2)

            node_capacity = self.calculate_final_node_capacity(randomized_source, randomized_sink)
            print(node_capacity)

            _distances = self._distances
            _flow = self._flow

            try:
                for node, node_ in cuts:
                    self.disconnect(node, node_)

                updated_partitions = self.partitions[:]

                print("len(cuts)", len(cuts))
                print("cuts", cuts)
                print("updated_partitions", len(updated_partitions))

                if (len(updated_partitions) != len(current_partitions) and expected_partition_increase is None) or (
                    expected_partition_increase is not None
                    and len(updated_partitions) != len(current_partitions) + expected_partition_increase
                ):
                    raise ValueError(
                        f"no cuts found for source ({randomized_source}) and sink ({randomized_sink}) that partitions the network like that"
                    )

                return len(cuts), cuts, updated_partitions
            except ValueError:
                continue
            finally:
                for node, node_ in cuts:
                    self.connect(node, node_)

                cuts = set()
                self._distances = _distances
                self._flow = _flow
                self._partitions = current_partitions

        raise ValueError(
            f"unable to find cuts that partitions the network after {tries} tries (expected cuts: {expected_cut_value}, expected partition increase: {expected_partition_increase})"
        )
        # break

        print("len(cuts)", len(cuts))
        print("cuts", cuts)
        print("updated_partitions", len(updated_partitions))

        return len(cuts), cuts, updated_partitions

        raise ValueError(
            f"unable to find cuts that partitions the network after {tries} tries (expected cuts: {expected_cut_value}, expected partition increase: {expected_partition_increase})"
        )

    def calculate_mincut_(
        self, source: NN | Node[NT, NC] | NT, sink: NN | Node[NT, NC] | NT, max_cut_value: int | None = None
    ) -> tuple[int, list[tuple[NN | Node[NT, NC], NN | Node[NT, NC]]], tuple[frozenset[NN], ...]]:
        if not isinstance(source, Node):
            source = self[source]
        if not isinstance(source, Node) or source.name not in self._nodes:
            raise ValueError(f'source node "{source.name}" not in network')

        if not isinstance(sink, Node):
            sink = self[sink]
        if not isinstance(sink, Node) or sink.name not in self._nodes:
            raise ValueError(f'sink node "{sink.name}" not in network')

        flow = self.calculate_flow(source, sink)
        keys = set()
        for key, flow_point in flow.items():
            # if (
            #    (key[0].name == "hfx" and key[1].name == "pzl")
            #    or (key[0].name == "bvb" and key[1].name == "cmg")
            #    or (key[0].name == "nvd" and key[1].name == "jqt")
            #    or (key[0].name == "pzl" and key[1].name == "hfx")
            #    or (key[0].name == "cmg" and key[1].name == "bvb")
            #    or (key[0].name == "jqt" and key[1].name == "nvd")
            # ):
            #    print(key, flow_point)
            #    keys.add(key)
            keys.add(key)
            if len(keys) == 8:
                break
        print(flow)
        print(list(flow.keys())[:6])
        print(keys)
        # breakpoint()
        # for i, flow_ in enumerate(itertools.permutations(list(flow.keys())[:6], 6)):
        skip_cuts = set()
        for i, flow_ in enumerate([key for key in itertools.permutations(keys, 3)]):
            print(flow_)
            current_partitions = self.partitions[:]
            cuts: set[tuple[NN | Node[NT, NC], NN | Node[NT, NC]]] = set()

            # print(f"calculate_mincut ({i:3d}):", flow_)
            try:
                while len(self.partitions) == len(current_partitions):
                    if max_cut_value and len(cuts) == max_cut_value:
                        raise ValueError(
                            f'no cuts found for source ("{source.name}") and sink ("{sink.name}") that partitions the network [1]'
                        )
                    for key in flow_:
                        if key in cuts:
                            continue
                        if key[0] == key[1]:
                            continue
                        self.disconnect(key[0], key[1])
                        cuts.add(key)
                        break
                    else:
                        if len(self.partitions) != len(current_partitions):
                            continue
                        # for node, node_ in cuts:
                        #    self.connect(node, node_)
                        raise ValueError(
                            f'no cuts found for source ("{source.name}") and sink ("{sink.name}") that partitions the network [2]'
                        )
            except ValueError as exc:
                print(str(exc))
                continue
            finally:
                self._should_recalculate_partitions = True
                updated_partitions = self.partitions[:]
                for node, node_ in cuts:
                    self.connect(node, node_)

            print("success:", len(cuts), cuts, len(updated_partitions))
            return len(cuts), cuts, updated_partitions

        raise ValueError(
            f'no cuts found for source ("{source.name}") and sink ("{sink.name}") that partitions the network [3]'
        )

        # graph = nx.Graph()
        # for node in self._nodes.values():
        #     graph.add_node(node.name)
        #     for node_ in node.nodes:
        #         graph.add_edge(node.name, node_.name, capacity=1)
        # cut_value, partition = nx.minimum_cut(graph, source.name, sink.name)
        # return cut_value, tuple(sorted([frozenset(self[node] for node in partition_) for partition_ in partition]))

    def __len__(self) -> int:
        return len(self._nodes)

    def __getitem__(self, name: NT) -> NN:
        if name not in self._nodes:
            raise KeyError(f"node {name} not found")
        return self._nodes[name]

    def __contains__(self, name: NT | NN) -> bool:
        return (name in self._nodes) or (name in self.nodes)

    def __repr__(self) -> str:
        network_name = f"{self.name} · " if self.name else ""
        nodes_str = " ".join([f"{node}" for node in self._nodes.values()])
        return f"network[{network_name}size: {len(self._nodes)} | nodes: {nodes_str} ::id:{hex(id(self))}]"

    def get(self, name: NT, default: object = None) -> NN | object:
        return self._nodes.get(name, default)


class NetworkPartition(Network):
    pass


async def run() -> int:
    # network = Network()
    # network.create_node("a", ["b", "e"])
    # network.create_node("b", ["c"])
    # network.create_node("c", ["d"])
    # network.create_node("e", ["d", "f", "g", "h"])
    # network.create_node("f", ["c"])

    # cut_value, cuts, partitions = network.find_mincut(expected_cut_value=3, expected_partition_increase=1)
    # print(network)
    # print(network.get("a").nodes)
    # print(network.get("a").input_nodes)

    # network.disconnect("b", "c")
    # network.disconnect("d", "e")
    # network.disconnect("f", "c")

    # flow = network.calculate_maximum_flow("a", "f")
    # print(flow)
    # print(network.partitions)

    # network.disconnect("c", "d")
    # network.disconnect("a", "e")
    # network.disconnect("f", "c")
    # print(network.partitions)
    # print(network["a"].nodes)

    # print("")
    # print("---")
    # print("")
    # return

    # network.create_node("c", ["d", "e", "k"])
    # network.create_node("d", ["e"])
    # network.create_node("e", ["c", "f", "l", "m"])
    # network.create_node("f", ["k", "b"])
    # print(network, len(network.partitions))
    # flow = network.calculate_flow("c", "f")
    # print(flow)
    # network.disconnect("e", "a")
    # print(network, len(network.partitions))
    # flow = network.calculate_flow("c", "f")
    # network.disconnect("d", "e")
    # print(flow)
    # print(network, len(network.partitions))
    # flow = network.calculate_flow("c", "f")
    # network.disconnect("e", "d")
    # print(flow)
    # print(network, len(network.partitions))
    # # network.disconnect("c", "d")
    # return

    # print(network)
    # print(network.calculate_flow("a", "b"))
    # return

    network = Network()
    # nodes = set()
    for component, *connections in values.alphanums():
        # print(len(network))
        # nodes.add(Node(component))
        network.create_node(component, connections)

    print(f"network created (size: {len(network)})")

    # print(network)
    # print(network.partitions)

    # flow = network.calculate_maximum_flow("jqt", "frs")
    # print(network)
    # flow = network.calculate_flow("jqt", "rhn")
    # print(flow)

    # cut_value, cuts, partitions = network.calculate_mincut("jqt", "frs")
    cut_value, cuts, partitions = network.find_mincut(expected_cut_value=3, expected_partition_increase=1)
    print("---")
    print("cuts:", cuts)
    print("---")
    # print("partitions:", partitions)
    # print("---")
    print("result = " + " * ".join([str(len(partition)) for partition in partitions]))
    print("---")

    result = 1
    for partition in partitions:
        result *= len(partition)

    return result

    # network.disconnect("cmg", "bvb")
    # print(network.calculate_maximum_flow("jqt", "frs"))
    # print("")
    # network.disconnect("hfx", "pzl")
    # print(network.calculate_maximum_flow("jqt", "frs"))
    # print("")

    # network.disconnect("hfx", "pzl")
    # network.disconnect("cmg", "bvb")
    # network.disconnect("jqt", "ntq")
    # network.disconnect("nvd", "pzl")
    # network.disconnect("jqt", "nvd")

    return

    # while True:
    #    network.

    # network.disconnect("cmg", "bvb")
    # network.disconnect("hfx", "pzl")
    # network.disconnect("jqt", "nvd")
    # partitions = network.partitions
    # values.partitions_count = (len(partitions[0]), len(partitions[1]))
    # return len(partitions[0]) * len(partitions[1])

    cut_value, cuts, partitions = network.find_mincut(expected_cut_value=3, expected_partition_increase=1)

    values.cut_value = cut_value
    values.cuts = cuts
    values.partitions_count = (len(partitions[0]), len(partitions[1]))

    return len(partitions[0]) * len(partitions[1])

    cut_value, cuts, partitions = network.calculate_mincut("qnr", "pzl")
    print(cut_value, cuts, partitions)
    # network.disconnect("cmg", "bvb")
    # network.disconnect("hfx", "pzl")
    # network.disconnect("jqt", "nvd")

    result = 1
    for partition in network.partitions:
        result *= len(partition)

    return result
    # network.disconnect("hfx", "pzl")
    # network.disconnect("bvb", "cmg")
    # network.disconnect("nvd", "jqt")
    # print(network, len(network.partitions))
    # print(network.partitions)
    # print(network.calculate_flow("qnr", "pzl"))
    return
    print(network, len(network.partitions))
    print(network.partitions)

    return
    graph = networkx.Graph()
    g = {}

    for l in values.rows:
        k, v = l.split(": ")
        v = v.split(" ")
        for vi in v:
            graph.add_edge(k, vi, capacity=1.0)
            g[k] = vi

    cut_value = 100
    while cut_value > 3:
        k1 = random.choice(list(graph.edges.keys()))[0]
        k2 = random.choice(list(graph.edges.keys()))[0]

        # bfs from k1 to k2
        cut_value, partition = networkx.minimum_cut(graph, k1, k2)

    print(partition)
    print(len(partition[0]) * len(partition[1]))
    return len(partition[0]) * len(partition[1])


# [values.year]            (number)  2023
# [values.day]             (number)  25
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day25/input
#
# Result: 559143
