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
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, TypeVar, Union

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

if False:
    # potential copy-pasta / quick inspiration

    # > regex (full match + transform)
    # input: "Object 123: R 3 sX 8 9 | L a++ m nn X k"
    # output: (123, ["R", "3", "sX", "8", "9"], ["L", "a++", "m", "nn", "X", "k"])
    for object_id_, part_1_, part_2_ in values.match_rows(
        r"^[^\d]*(\d+):\s*(.*)\s*[|]\s*(.*)\s*$", transform=(int, str.split, str.split)
    ):
        pass

    # > regex (find all + transform)
    # input: "1  -  1, 48, 83, 86, 17; 83, 86,  6, 31, 17,  9, 48, 53"
    # output: (1, {1, 48, 17, 83, 86}, {6, 9, 48, 17, 83, 53, 86, 31})
    parse_numbers_ = lambda v_: set(map(int, v_.split(", ")))
    for single_, setpart_1_, setpart_2_ in values.findall_rows(
        r"((?:\d+(?:,\s+|)?)+)", transform=(int, parse_numbers_, parse_numbers_)
    ):
        pass

    # > multisplit
    # input: "a, b, c; d, e, f; g, h, i"
    # output: [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]
    result_ = multisplit(values.input, ["; ", ", "])

    # > inverse dict (flip key and value)
    # input: ["7 red", "3 green", "8 blue"]
    # output: {'red': 7, 'green': 3, 'blue': 8}
    result_ = inverse_dict(map(str.split, values.rows), transform=(str, int))

    # > add tuple elements (good for vectors, positions, coordinates)
    result_ = tuple_add((1, 2), (-1, 0))  # (0, 2)
    result_ = tuple_add((1, 2), (1, -1))  # (2, 1)

    # > get nearby vectors (positions) in a grid
    pos = (5, 6)
    for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
        pos_ = tuple_add(pos, mod)

    # > Counter operations
    # input: "123ABC1232"
    # output: [('2', 3), ('1', 2), ('3', 2), ('A', 1), ('B', 1), ('C', 1)]
    Counter("123ABC1232").most_common()

    # > other useful methods
    values.findall_int()
    values.findall_alphanum()


# https://docs.python.org/3/library/itertools.html
# https://docs.python.org/3/library/collections.html


# To accurately tackle this problem, let's break down the requirements and details:
#
# We have a wiring diagram represented as a list of connections between components.
# Each line represents one component and the components it is connected to.
# We are to find only three wires to disconnect such that the equipment is divided into two disconnected groups.
# The aim is to multiply the sizes of these two groups together to get the final result.
# The connections are not directional; abc: xyz means the same as xyz: abc.
# Each connection is unique and only represented once in the entire input diagram.
# Before coding, let's reason through potential steps to solve the challenge:
#
# Graph Representation: Since this is a connectivity problem, it's natural to model the wiring diagram as a graph where nodes represent components and edges represent wires.
# Find Critical Connections: What we're looking for is akin to bridge edges in the graph, removing which would split the graph into disconnected subgraphs.
# Minimize Edge Removal: Since we only need to remove three edges to achieve the task, we are looking for the minimum number of edges whose removal leads to the largest difference in the sizes of the resulting subgraphs, provided that the total number of disconnected components is minimized (since we need to half at least half of the equipment disconnected).
# Trial and Removal: We might need to try removing sets of three connections and measure their impact on the graph. Then, we keep the try that leads to the desired outcome.
# Group Size Calculation: Once we've disconnected the components, we need to traverse the resulting subgraphs to calculate their sizes.
# Final Computation: The final step is to multiply the sizes of the two separate groups and get the result.
# Next, we will have to analyze actual puzzle input, which we don't yet have. To proceed further, please provide the puzzle input so that we can work on crafting the exact Python solution for this challenge.


def find_optimal_disconnect_combination(graph):
    # Function to find the number of components in a group starting from a given node
    def dfs(node, visited, temp_graph):
        visited.add(node)
        for neighbor in temp_graph[node]:
            if neighbor not in visited:
                dfs(neighbor, visited, temp_graph)

    # Function to count components in two groups after disconnecting a set of edges
    def count_groups_after_disconnecting(edges_to_disconnect, original_graph):
        # Create a copy of the graph
        temp_graph = {node: set(neighbors) for node, neighbors in original_graph.items()}

        # Remove the edges
        for a, b in edges_to_disconnect:
            temp_graph[a].discard(b)
            temp_graph[b].discard(a)

        # Find the two groups
        visited = set()
        groups = []
        for node in temp_graph:
            if node not in visited:
                group = set()
                dfs(node, group, temp_graph)
                groups.append(group)
                visited.update(group)

        # Return sizes of the two groups if there are exactly two
        return [len(g) for g in groups] if len(groups) == 2 else None

    # Generate all combinations of three edges to disconnect
    edges = set()
    for node in graph:
        for neighbor in graph[node]:
            if (neighbor, node) not in edges:  # Avoid duplicates
                edges.add((node, neighbor))

    best_group_sizes = None
    best_difference = float("inf")

    for combo in combinations(edges, 3):
        group_sizes = count_groups_after_disconnecting(combo, graph)
        if group_sizes:
            difference = abs(group_sizes[0] - group_sizes[1])
            if difference < best_difference:
                best_difference = difference
                best_group_sizes = group_sizes

    return best_group_sizes


import sys
from collections import defaultdict

sys.setrecursionlimit(1000000)


# Function to find all connected components in a graph using DFS
def find_connected_components(graph):
    visited = set()

    def dfs(component):
        visited.add(component)
        component_size = 1
        for neighbor in graph[component]:
            if neighbor not in visited:
                component_size += dfs(neighbor)
        return component_size

    components_sizes = []
    for component in graph:
        if component not in visited:
            components_sizes.append(dfs(component))

    return components_sizes


# Function to generate all edges in the graph
def get_all_edges(graph):
    edges = set()
    for component, neighbors in graph.items():
        for neighbor in neighbors:
            # Ensure (component, neighbor) and (neighbor, component) are treated as the same edge
            edge = tuple(sorted([component, neighbor]))
            edges.add(edge)
    return edges


def parse_wiring_diagram(diagram):
    graph = defaultdict(set)

    for line in diagram.strip().split("\n"):
        component, connections = line.split(": ")
        connections = connections.split()
        graph[component].update(connections)
        for conn in connections:
            graph[conn].add(component)

    return graph


# graph = parse_wiring_diagram(values.input)
# all_edges = get_all_edges(graph)
# all_edges_combinations = combinations(all_edges, 3)  # All combinations of three edges.

# Now let's find out the combination of three edges that when removed, divides the graph into two subgraphs
# where the product of the sizes of these two subgraphs is as large as possible, and at least half of the components are disconnected.


def disconnect_edges_and_find_sizes(graph, edges_to_remove):
    # Create a copy of the graph
    modified_graph = defaultdict(set, {k: set(v) for k, v in graph.items()})

    # Remove the specified edges
    for edge in edges_to_remove:
        modified_graph[edge[0]].remove(edge[1])
        modified_graph[edge[1]].remove(edge[0])

    # Find connected components of the modified graph
    components_sizes = find_connected_components(modified_graph)
    return components_sizes


# Find the best combination of edge removals
# best_product = 0
# best_combination = None
#
# for edges_combination in all_edges_combinations:
#     # Get the sizes of the connected components after removing the edges
#     components_sizes = disconnect_edges_and_find_sizes(graph, edges_combination)
#
#     # We are looking for exactly two separate groups
#     if len(components_sizes) == 2:
#         # Calculate the product of the sizes of the two groups
#         product = components_sizes[0] * components_sizes[1]
#         # Check if we have a better product than what we've found so far
#         if product > best_product:
#             best_product = product
#             best_combination = edges_combination
#
# print(best_product, best_combination)

from typing import Collection, Generic, Hashable, Iterable, MutableSet, Self, Sequence, Sized, TypeVar

NT = TypeVar("NT", bound=Hashable)
NC = TypeVar("NC", bound=Collection)
NN = TypeVar("NN", bound="Node")


class Node(Generic[NT, NC]):
    _id: NT
    _nodes: Collection[NT]
    _network: "Network[Node[NT, NC], NT, NC] | None"
    _storage: dict[str, Any]

    def __new__(cls, id_: NT, *, network: "Network | None" = None, without_network: bool = False):
        self = super().__new__(cls)

        self._id = id_
        self._nodes = set()
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
        if self.name not in node._nodes:
            node.add_node(self)

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

    def add_nodes(self, nodes: Collection["Node[NT, NC]"]) -> None:
        for node in nodes:
            self.add_node(node)

    @property
    def nodes(self) -> Collection["Node[NT, NC]"]:
        if not self._network:
            raise ValueError("node not in network (use node._nodes instead)")
        return {self._network[node] for node in self._nodes}

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
                self._network[node].disconnect_node(self)

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
                            if node_ is node:
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
        return

        nodes = set(self._nodes.values())
        partitions: list[set[Node]] = []
        partitions.append(nodes)

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

                        if node not in self.nodes and node._network == self:
                            raise Exception("node not in network.nodes, but node._network is set to network")

                        if node in self.nodes and node._network != self:
                            raise Exception("node in network.nodes, but node._network is not network")

                        for node_ in node.nodes:
                            if node_ is node:
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

                    node_union: set[Node] = {next(iter(partition))}
                    processed_nodes: set[Node] = set()
                    while node_union - processed_nodes:
                        node = next(iter(node_union - processed_nodes))
                        processed_nodes.add(node)
                        node_union |= set(node.nodes)

                    if node_union != partition:
                        # print(partition, "|", node_union, "|", (node_union & partition), "|", (partition - node_union))
                        if node_union & partition == partition and node_union & partition == node_union:
                            partitions.remove(partition)
                            if node_union in partitions:
                                partitions.remove(node_union)
                            partitions.append(partition | node_union)
                            raise RecalculatePartitionsError
                        elif (node_union - partition) & (partition - node_union):
                            partitions.remove(partition)
                            if node_union in partitions:
                                partitions.remove(node_union)
                            partitions.append(partition ^ node_union)
                            partitions.append(partition & node_union)
                            raise RecalculatePartitionsError
                        else:
                            partitions.remove(partition)
                            if node_union in partitions:
                                partitions.remove(node_union)
                            partitions.append(node_union)
                            partitions.append(partition - node_union)
                            raise RecalculatePartitionsError

            except RecalculatePartitionsError:
                continue

            break

        self._partitions = sorted([frozenset(partition) for partition in partitions], key=len)

    def calculate_flow(
        self, source: NN | Node[NT, NC] | NT, sink: NN | Node[NT, NC] | NT
    ) -> dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], int]:
        if not isinstance(source, Node):
            source = self[source]
        if not isinstance(source, Node) or source.name not in self._nodes:
            raise ValueError(f'source node "{source.name}" not in network')

        if not isinstance(sink, Node):
            sink = self[sink]
        if not isinstance(sink, Node) or sink.name not in self._nodes:
            raise ValueError(f'sink node "{sink.name}" not in network')

        queue: list = []  # e: list[tuple[int, NN | Node[NT, NC], set[NN | Node[NT, NC]], tuple[NN | Node[NT, NC], ...]]] = []
        all_visited: set[NN | Node[NT, NC]] = set()

        def enqueue(
            queue: list | set,
            node: NN | Node[NT, NC],
            prev: NN | Node[NT, NC],
            visited: set[NN | Node[NT, NC]],
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

            sort_key = -len(visited)

            qdata = (sort_key, node, prev, frozenset(visited))
            # heapq.heappush(queue, (-len(visited), node_, node, visited | {node_}, (*path, node_), 100))
            if isinstance(queue, set):
                queue.add(qdata)
            else:
                heapq.heappush(queue, qdata)

            # heapq.heappush(queue, (sort_key, node, prev, frozenset(visited)))

        def convert_queue(
            queue: list | set,
        ) -> list | set:
            if isinstance(queue, set):
                queue = list(queue)
                heapq.heapify(queue)
            elif isinstance(queue, list):
                queue = set(queue)
            return queue

        flow: dict[tuple[NN | Node[NT, NC], NN | Node[NT, NC]], int] = {}
        total_queued_count: int = 0
        source_sink_max_distance = float("inf")
        source_sink_min_distance = float("inf")

        # enqueue(source, source, {source})
        # queue.append((source, {source}, (source,)))

        # queue = set()
        # queue.add((0, source, source, frozenset({source})))
        enqueue(queue, source, source, {source})
        #        heapq.heappush(queue, (-total_queued_count, source, source, {source}))
        while queue:
            # queue = heapq.nsmallest(500, queue)

            # sort_key, node, prev, visited, path, score = heapq.heappop(queue)
            # data = queue.pop()
            # print(data)
            if isinstance(queue, set):
                _, node, prev, visited = queue.pop()
            else:
                _, node, prev, visited = heapq.heappop(queue)

            all_visited.add(node)

            if len(visited) > source_sink_max_distance * 2:
                continue

            if total_queued_count > 100000 and source_sink_max_distance > 2000:
                if isinstance(queue, list):
                    print(len(queue))
                    queue = heapq.nsmallest(100, queue)
                    print(len(queue))
                    queue = convert_queue(queue)
                    print(len(queue))
                else:
                    print(len(queue))
                    queue = set(heapq.nsmallest(100, list(queue)))
                    print(len(queue))
                breakpoint()

            if total_queued_count > 100000 and node in all_visited:
                continue

            if total_queued_count > 300000:
                break
            # print(sort_key)

            # if total_queued_count % 20000 == 0:
            #    print(total_queued_count, len(queue), len(flow), score)
            # queue = heapq.nsmallest(500, queue)
            # total_queued_count += 1
            # return {v_: k_ for k_, v_ in sorted([(v, k) for k, v in flow.items()], reverse=True)}

            # print(len(queue), sort_key)
            if node is sink:
                source_sink_max_distance = (
                    len(visited)
                    if source_sink_max_distance == float("inf")
                    else max(source_sink_max_distance, len(visited))
                )
                source_sink_min_distance = min(source_sink_min_distance, len(visited))

                print(
                    f"{sink} is the sink: visited through {len(visited)} nodes (min: {source_sink_min_distance} | max: {source_sink_max_distance}) :: quuee: {len(queue)}"
                )

                if source_sink_max_distance >= 50:
                    if isinstance(queue, list):
                        queue = heapq.nsmallest(2**source_sink_max_distance, queue)
                        queue = convert_queue(queue)
                    else:
                        queue = set(heapq.nsmallest(2**source_sink_max_distance, list(queue)))
                        enqueue(queue, source, source, {source})

                # queue = heapq.nsmallest(100, queue)
                # queue = [is
                # queue.add((0, source, source, frozenset({source}), (source,), 0))

                # if node is sink:
                #     sink_ = source
                #     source_ = sink
                #     sink = source_
                #     source = sink_
                #                    sink, source = source, sink
                # enqueue(source, source, {source}, (source,), 0)
                # elif node is source:
                #    sink = sink
                #    enqueue(source, source, {source}, (source,), 0)

                # print("node is sink", sink, sort_key, len(queue))
                # path = tuple(visited)
                path = list(visited)
                # print("visited", len(visited), source, visited, sink)
                for i, key in enumerate(list(zip(path, path[1:]))):
                    flow[key] = flow.get(key, 1) + 100 * 1.01
                # for i, node in enumerate(path):
                #     for node_ in visited:
                #         key = (node, node_)
                #         if node_ in (node.nodes & visited):
                #             flow[key] = flow.get(key, 1) + 3000
                #         else:
                #             flow[key] = flow.get(key, 1) - 2000

                # queue = set()
                # queue.add((source, source, frozenset({source})))

                continue
                # for i, key in enumerate(zip(path, path[1:])):
                #     flow[key] = flow.get(key, 0) + 1
                # continue

            # score += len(node.nodes & (visited - {prev})) * 10

            # flow[key] = flow.get(key, 1) + 1
            # score = flow.get(key, 0)

            # if len(node.nodes & (visited - {prev})) > 0:
            #     # print(len(visited), path)
            #     # non optimal path
            #     # print("non optimal")
            #     # print(node.nodes & visited)
            #     # print("is visited:", prev)
            #     # continue
            # continue
            #    continue
            # nodes_ = node.nodes  # set(random.choices(list(node.nodes)) if total_queued_count > 1000 else node.nodes)
            for node_ in node.nodes:
                if node_ in visited:
                    continue
                # key = (node, node_)
                # flow[key] = flow.get(key, 0) + 1
                # enqueue(node_, node, visited | {node_}, (), score)  # , (*path, node_))

                # key = (node, node_)
                # if flow.get(key, 0) > 0:
                #     continue
                # key = (node_, node)
                # if flow.get(key, 0) > 0:
                #     continue

                enqueue(queue, node_, node, visited | {node_})

                total_queued_count += 1
                if total_queued_count % 10000 == 0:
                    print(total_queued_count, len(queue))

        #             if total_queued_count >= 500000 and total_queued_count < 600000:
        #                 queue = []
        #                 early_flow = {v_: k_ for k_, v_ in sorted([(v, k) for k, v in flow.items()][:30], reverse=True)}
        #                 new_workers = 10
        #                 heapq.heappush(queue, (-total_queued_count, source, source, frozenset({source})))
        #                 for key, value in early_flow.items():
        #                     if value > 0:
        #                         if new_workers > 0:
        #                             new_workers -= 1
        #                         if isinstance(queue, set):
        #                             queue.add((0, key[0], key[1], frozenset({key[0], key[1]})))
        #                             queue.add((0, key[1], key[0], frozenset({key[0], key[1]})))
        #                         else:
        #                             heapq.heappush(queue, (-total_queued_count, key[0], key[1], frozenset({key[0], key[1]})))
        #                             heapq.heappush(queue, (-total_queued_count, key[1], key[0], frozenset({key[0], key[1]})))
        #                 total_queued_count = 600000
        #                 continue
        #             if total_queued_count >= 1500000:
        #                 break
        #                 # enqueue(node_, node, visited | {node_})
        #                 # break
        #                 # print(len(visited))
        #
        #                 # queue.append((node_, visited | {node_}, (*path, node_)))

        return {v_: k_ for k_, v_ in sorted([(v, k) for k, v in flow.items()], reverse=True)[:30]}

    def find_mincut(
        self, expected_cut_value: int, expected_partition_increase: int = 1
    ) -> tuple[int, list[tuple[NN | Node[NT, NC], NN | Node[NT, NC]]], tuple[frozenset[NN], ...]]:
        tries = 0
        current_partitions = self.partitions[:]
        bad_choices: set[tuple[NN, NN]] = set()
        while True:
            randomized_source = random.choice(list(self._nodes.values()))
            randomized_sink = random.choice(list(self._nodes.values()))

            if (randomized_source, randomized_sink) in bad_choices:
                continue

            tries += 1

            # print("randomized_source", randomized_source)
            # print("randomized_sink", randomized_sink)

            if randomized_source == randomized_sink:
                continue

            try:
                cut_value, cuts, updated_partitions = self.calculate_mincut(
                    randomized_source, randomized_sink, expected_cut_value
                )
            except ValueError as exc:
                bad_choices.add((randomized_source, randomized_sink))
                print(tries, "fail", str(exc))
                continue

            print("find_mincut", tries, cut_value, len(updated_partitions), cuts)

            if cut_value != expected_cut_value:
                continue
            if len(updated_partitions) != len(current_partitions) + expected_partition_increase:
                continue

            return cut_value, cuts, updated_partitions

    def calculate_mincut(
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
    # network = Network[Node[str, set], str, set]()
    # network.create_node("a", ["b", "e"])
    # network.create_node("b", ["c"])
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
    nodes = set()
    for component, *connections in values.alphanums():
        print(len(network))
        # nodes.add(Node(component))
        network.create_node(component, connections)

    print("network created")
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

    def parse_wiring_diagram(diagram):
        graph = defaultdict(set)

        for line in diagram.strip().split("\n"):
            component, connections = line.split(": ")
            connections = connections.split()
            graph[component].update(connections)
            for conn in connections:
                graph[conn].add(component)

        return graph

    def optimize_disconnect_combination(graph):
        # Use a modified depth-first search to find critical edges
        def dfs(node, visited, parent, low, disc, time, bridges):
            visited.add(node)
            disc[node] = low[node] = time[0]
            time[0] += 1

            for neighbor in graph[node]:
                if neighbor not in visited:
                    parent[neighbor] = node
                    dfs(neighbor, visited, parent, low, disc, time, bridges)
                    low[node] = min(low[node], low[neighbor])
                    if low[neighbor] > disc[node]:
                        bridges.append((node, neighbor))
                elif neighbor != parent[node]:
                    low[node] = min(low[node], disc[neighbor])

        # Initialize arrays for DFS
        visited = set()
        disc = {node: float("inf") for node in graph}  # Discovery times
        low = {node: float("inf") for node in graph}  # Earliest visited vertex
        parent = {node: None for node in graph}
        time = [0]
        bridges = []

        # Run DFS to find bridges (critical edges)
        for node in graph:
            if node not in visited:
                dfs(node, visited, parent, low, disc, time, bridges)

        # Sort bridges by the degree of their nodes (prioritize higher degree nodes)
        bridges.sort(key=lambda edge: max(len(graph[edge[0]]), len(graph[edge[1]])), reverse=True)

        # Test disconnecting combinations of the top bridges
        for combo in combinations(bridges[:10], 3):  # Limit to top 10 bridges to reduce computation
            group_sizes = count_groups_after_disconnecting(combo, graph)
            if group_sizes:
                return group_sizes

        return None

    def heuristic_disconnect_combination_corrected(graph):
        # Modified DFS to calculate group size
        def dfs_size(node, visited, temp_graph):
            visited.add(node)
            size = 1
            for neighbor in temp_graph[node]:
                if neighbor not in visited:
                    size += dfs_size(neighbor, visited, temp_graph)
            return size

        # Heuristic function to estimate the best wires to disconnect
        def find_best_disconnect(graph):
            # Start by finding all edges
            edges = {(a, b) for a in graph for b in graph[a] if a < b}

            best_disconnect = None
            smallest_diff = float("inf")

            print(len(edges))

            print(len(list(combinations(edges, 3))))
            return

            # Iteratively test disconnecting each set of three wires
            for combo in combinations(edges, 3):
                # Create a copy of the graph
                temp_graph = {node: set(neighbors) for node, neighbors in graph.items()}

                # Disconnect the wires in the combo
                for a, b in combo:
                    temp_graph[a].discard(b)
                    temp_graph[b].discard(a)

                # Check the sizes of the two resulting groups
                visited = set()
                first_group_size = dfs_size(next(iter(temp_graph)), visited, temp_graph)

                # Ensure there are unvisited nodes before the second DFS traversal
                unvisited_nodes = set(temp_graph.keys()) - visited
                if unvisited_nodes:
                    second_group_size = dfs_size(next(iter(unvisited_nodes)), visited, temp_graph)
                else:
                    continue  # Skip this combination if all nodes were visited in the first DFS

                # Calculate the difference in sizes
                diff = abs(first_group_size - second_group_size)
                if diff < smallest_diff:
                    smallest_diff = diff
                    best_disconnect = (first_group_size, second_group_size)

                # Early exit if an equal split is found
                if diff == 0:
                    break

            return best_disconnect

        return find_best_disconnect(graph)

    def efficient_disconnect_combination(graph):
        # Function to calculate the centrality of an edge
        def edge_centrality(edge):
            # Centrality based on the degrees of the nodes it connects
            return len(graph[edge[0]]) + len(graph[edge[1]])

        # Function to find the largest component's size after disconnecting an edge
        def component_size_after_disconnect(node, temp_graph):
            visited = set()
            return dfs_size(node, visited, temp_graph)

        # Modified DFS to calculate group size
        def dfs_size(node, visited, temp_graph):
            visited.add(node)
            size = 1
            for neighbor in temp_graph[node]:
                if neighbor not in visited:
                    size += dfs_size(neighbor, visited, temp_graph)
            return size

        # Find all edges and sort them by their centrality
        edges = [(a, b) for a in graph for b in graph[a] if a < b]
        edges.sort(key=edge_centrality, reverse=True)
        print(len(edges))

        # Try disconnecting edges one by one, focusing on the most central ones
        for edge in edges:
            temp_graph = {node: set(neighbors) for node, neighbors in graph.items()}
            temp_graph[edge[0]].discard(edge[1])
            temp_graph[edge[1]].discard(edge[0])

            # Calculate the size of the largest component after disconnecting the edge
            largest_component_size = component_size_after_disconnect(next(iter(temp_graph)), temp_graph)

            # Check if disconnecting this edge splits the graph into two nearly equal parts
            if abs(largest_component_size - (len(graph) - largest_component_size)) <= 1:
                return (largest_component_size, len(graph) - largest_component_size)

        return None

    graph = parse_wiring_diagram(values.input)

    optimal_group_sizes = heuristic_disconnect_combination_corrected(graph)
    result = 1
    for i in optimal_group_sizes:
        result = result * i
    return result

    # Reuse the count_groups_after_disconnecting function from earlier
    # Test the optimized function with the example diagram
    optimized_group_sizes = optimize_disconnect_combination(graph)
    return optimized_group_sizes

    # Test the optimized function with the example diagram
    optimal_group_sizes = find_optimal_disconnect_combination(graph)

    result = 1
    for i in optimal_group_sizes:
        result = result * i
    return result
    result = 0

    for row in values:
        pass

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  25
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day25/input
#
# Result: 559143
