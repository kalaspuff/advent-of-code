# note to self: rewriting and cleaning up to work with example + actual puzzle input as they different approaches (at least the way I've solved this)
# lots of temporary code and broken stuff at the moment.

import heapq
from itertools import cycle, islice

from helpers import (
    find_cyclic_pattern,
    find_layered_cyclic_pattern,
    sequence_delta_layers,
    sequence_delta_offset,
    sequence_offset_sum,
    sum_sequence,
    tuple_add,
)
from values import values

# (x, y) - right, down, left, up
DIRECTIONS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))


# def calculate_cycle_length(results: list[int]) -> int:
#     return 0
#
#
# def find_cyclic_pattern(sequence: list[int] | tuple[int, ...], max_pattern_length: int = 10) -> list[int] | None:
#     for pattern_length in range(2, max_pattern_length + 1):
#         pattern = sequence[-pattern_length:]
#         sequence_ = sequence[-pattern_length * 3 :]
#         if list(islice(cycle(pattern), len(sequence_))) == sequence_:
#             return pattern
#     return None
#
#
# def sequence_offset_delta(sequence: list[int] | tuple[int, ...], offset: int = 1) -> list[int]:
#     return [sequence[i + offset] - sequence[i] for i in range(len(sequence) - offset)]
#
#
# def sequence_offset_sum(sequence: list[int] | tuple[int, ...], offset: int = 1) -> list[int]:
#     return [sequence[i + offset] + sequence[i] for i in range(len(sequence) - offset)]
#
#
# def sum_sequence(
#     *sequence: list[int]
#     | list[list[int] | tuple[int, ...]]
#     | tuple[int, ...]
#     | tuple[list[int] | tuple[int, ...], ...],
# ) -> list[int]:
#     sequences: list[list[int]] = []
#     for seq in sequence:
#         if (
#             isinstance(seq, (list, tuple))
#             and len(seq)
#             and isinstance(seq[0], (list, tuple))
#             and len(seq[0])
#             and isinstance(seq[0][0], int)
#             and not isinstance(seq, int)
#         ):
#             for sub_seq in seq:
#                 if isinstance(sub_seq, int):
#                     raise ValueError(f"Invalid sequence: {seq}")
#                 for sub_seq_ in sub_seq:
#                     if not isinstance(sub_seq_, int):
#                         raise ValueError(f"Invalid sequence: {seq}")
#                 sequences.append([s for s in sub_seq if isinstance(s, int)])
#         elif isinstance(seq, (list, tuple)) and len(seq) and isinstance(seq[0], int):
#             for sub_seq in seq:
#                 if not isinstance(sub_seq, int):
#                     raise ValueError(f"Invalid sequence: {seq}")
#             sequences.append([s for s in seq if isinstance(s, int)])
#         else:
#             raise ValueError(f"Invalid sequence: {seq}")
#     print(sequences)
#     print(list(zip(*sequences)))
#     return [sum(*v) for v in zip(sequences)]


async def run() -> int:
    pos = start_pos = values.matrix.position("S")[0]
    matrix = values.matrix.replace("S", ".")
    possible_positions = set(matrix.position("."))
    width, height = matrix.width, matrix.height
    max_steps = 1000

    steps = 0
    queue = {start_pos}
    results = []
    while steps < max_steps:
        steps += 1
        visited: set[tuple[int, int]] = set()

        while queue:
            pos = queue.pop()

            for mod in DIRECTIONS:
                pos_ = tuple_add(pos, mod)
                normalized_pos = (pos_[0] % width, pos_[1] % height)
                if normalized_pos not in possible_positions:
                    continue

                visited.add(pos_)

                # key = pos_
                # if key in visited:
                #     continue

            #    queue.add(key)

        queue = visited
        reachable_count = len(queue)
        results.append(reachable_count)

        if steps > 20:
            sequences, layer, cycle_length, pattern = find_layered_cyclic_pattern(
                results, 10, range(3, 41), range(3, 41)
            )
            if pattern:
                print("pattern in layer:", layer)
                print("cycle_length:", cycle_length)
                print("pattern:", pattern)

            # if not sequences:
            #    sequences = sequence_delta_layers(results, 7, 11)
            for i, seq in enumerate(sequences):
                print(f"layer {i}:", seq[-20:])
            # print(sequences)
            # delta_1 = sequence_offset_delta(results)
            print("steps:", steps, "result:", len(queue))

    result = len(queue)

    for pos in visited:
        normalized_pos = (pos[0] % width, pos[1] % height)
        matrix[normalized_pos] = "O"

    values.matrix_count = matrix.count("O")
    return result


# [values.year]            (number)  2023
# [values.day]             (number)  21
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day21/input
#
# Result: 609585229256084


#
# import functools
# import itertools
# import math
# import re
# from collections import Counter, deque
# from itertools import combinations, permutations, product
# from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, TypeVar, Union
#
# import helpers
# from helpers import (
#     Range,
#     Ranges,
#     batched,
#     inverse,
#     inverse_dict,
#     manhattan_distance,
#     multisplit,
#     paired,
#     pairwise,
#     position_ranges,
#     transform,
#     transform_dict,
#     transform_tuple,
#     tuple_add,
# )
# from matrix import Matrix
# from values import Values, values
#
# if False:
#     # potential copy-pasta / quick inspiration
#
#     # > regex (full match + transform)
#     # input: "Object 123: R 3 sX 8 9 | L a++ m nn X k"
#     # output: (123, ["R", "3", "sX", "8", "9"], ["L", "a++", "m", "nn", "X", "k"])
#     for object_id_, part_1_, part_2_ in values.match_rows(
#         r"^[^\d]*(\d+):\s*(.*)\s*[|]\s*(.*)\s*$", transform=(int, str.split, str.split)
#     ):
#         pass
#
#     # > regex (find all + transform)
#     # input: "1  -  1, 48, 83, 86, 17; 83, 86,  6, 31, 17,  9, 48, 53"
#     # output: (1, {1, 48, 17, 83, 86}, {6, 9, 48, 17, 83, 53, 86, 31})
#     parse_numbers_ = lambda v_: set(map(int, v_.split(", ")))
#     for single_, setpart_1_, setpart_2_ in values.findall_rows(
#         r"((?:\d+(?:,\s+|)?)+)", transform=(int, parse_numbers_, parse_numbers_)
#     ):
#         pass
#
#     # > multisplit
#     # input: "a, b, c; d, e, f; g, h, i"
#     # output: [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]
#     result_ = multisplit(values.input, ["; ", ", "])
#
#     # > inverse dict (flip key and value)
#     # input: ["7 red", "3 green", "8 blue"]
#     # output: {'red': 7, 'green': 3, 'blue': 8}
#     result_ = inverse_dict(map(str.split, values.rows), transform=(str, int))
#
#     # > add tuple elements (good for vectors, positions, coordinates)
#     result_ = tuple_add((1, 2), (-1, 0))  # (0, 2)
#     result_ = tuple_add((1, 2), (1, -1))  # (2, 1)
#
#     # > get nearby vectors (positions) in a grid
#     pos = (5, 6)
#     for mod in itertools.product([-1, 0, 1], [-1, 0, 1]):
#         pos_ = tuple_add(pos, mod)
#
#     # > Counter operations
#     # input: "123ABC1232"
#     # output: [('2', 3), ('1', 2), ('3', 2), ('A', 1), ('B', 1), ('C', 1)]
#     Counter("123ABC1232").most_common()
#
#     # > other useful methods
#     values.findall_int()
#     values.findall_alphanum()
#
#
# # https://docs.python.org/3/library/itertools.html
# # https://docs.python.org/3/library/collections.html
#
#
# def find_starting_position(grid):
#     for y, row in enumerate(grid):
#         for x, cell in enumerate(row):
#             if cell == "S":
#                 return (x, y)
#     return None
#
#
# def count_reachable_plots(grid, steps):
#     start = find_starting_position(grid)
#     if not start:
#         return 0
#
#     directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, E, S, W
#     visited = set()
#     queue = deque([(start, 0)])
#     reached = set()
#
#     while queue:
#         position, step = queue.popleft()
#
#         if step == steps:
#             reached.add(position)
#             continue
#
#         for dx, dy in directions:
#             nx, ny = position[0] + dx, position[1] + dy
#             if (
#                 0 <= nx < len(grid[0])
#                 and 0 <= ny < len(grid)
#                 and grid[ny][nx] == "."
#                 and ((nx, ny), step + 1) not in visited
#             ):
#                 visited.add(((nx, ny), step + 1))
#                 queue.append(((nx, ny), step + 1))
#
#     return len(reached)
#
#
# cyclic_pattern = [
#     (1, 1),
#     (2, 2),
#     (3, 4),
#     (4, 6),
#     (5, 9),
#     (6, 13),
#     (7, 16),
#     (8, 22),
#     (9, 30),
#     (10, 41),
#     (11, 50),
#     (12, 63),
#     (13, 74),
#     (14, 89),
#     (15, 99),
#     (16, 115),
#     (17, 129),
#     (18, 145),
#     (19, 165),
#     (20, 192),
#     (21, 216),
#     (22, 234),
#     (23, 261),
#     (24, 294),
#     (25, 326),
#     (26, 353),
#     (27, 395),
#     (28, 427),
#     (29, 460),
#     (30, 491),
#     (31, 537),
#     (32, 574),
#     (33, 605),
#     (34, 644),
#     (35, 689),
#     (36, 740),
#     (37, 784),
#     (38, 846),
#     (39, 894),
#     (40, 944),
#     (41, 989),
#     (42, 1053),
#     (43, 1107),
#     (44, 1146),
#     (45, 1196),
#     (46, 1256),
#     (47, 1324),
#     (48, 1383),
#     (49, 1464),
#     (50, 1528),
#     (51, 1594),
#     (52, 1653),
#     (53, 1735),
#     (54, 1805),
#     (55, 1853),
#     (56, 1914),
#     (57, 1988),
#     (58, 2072),
#     (59, 2145),
#     (60, 2244),
#     (61, 2324),
#     (62, 2406),
#     (63, 2479),
#     (64, 2579),
#     (65, 2665),
#     (66, 2722),
#     (67, 2794),
#     (68, 2882),
#     (69, 2982),
#     (70, 3069),
#     (71, 3186),
#     (72, 3282),
#     (73, 3380),
#     (74, 3467),
#     (75, 3585),
#     (76, 3687),
#     (77, 3753),
#     (78, 3836),
#     (79, 3938),
#     (80, 4054),
#     (81, 4155),
#     (82, 4290),
#     (83, 4402),
#     (84, 4516),
#     (85, 4617),
#     (86, 4753),
#     (87, 4871),
#     (88, 4946),
#     (89, 5040),
#     (90, 5156),
#     (91, 5288),
#     (92, 5403),
#     (93, 5556),
#     (94, 5684),
#     (95, 5814),
#     (96, 5929),
#     (97, 6083),
#     (98, 6217),
#     (99, 6301),
#     (100, 6406),
#     (101, 6536),
#     (102, 6684),
#     (103, 6813),
#     (104, 6984),
#     (105, 7128),
#     (106, 7274),
#     (107, 7403),
#     (108, 7575),
#     (109, 7725),
#     (110, 7818),
#     (111, 7934),
#     (112, 8078),
#     (113, 8242),
#     (114, 8385),
#     (115, 8574),
#     (116, 8734),
#     (117, 8896),
#     (118, 9039),
#     (119, 9229),
#     (120, 9395),
#     (121, 9497),
#     (122, 9624),
#     (123, 9782),
#     (124, 9962),
#     (125, 10119),
#     (126, 10326),
#     (127, 10502),
#     (128, 10680),
#     (129, 10837),
#     (130, 11045),
#     (131, 11227),
#     (132, 11338),
#     (133, 11476),
#     (134, 11648),
#     (135, 11844),
#     (136, 12015),
#     (137, 12240),
#     (138, 12432),
#     (139, 12626),
#     (140, 12797),
#     (141, 13023),
#     (142, 13221),
#     (143, 13341),
#     (144, 13490),
#     (145, 13676),
#     (146, 13888),
#     (147, 14073),
#     (148, 14316),
#     (149, 14524),
#     (150, 14734),
#     (151, 14919),
#     (152, 15163),
#     (153, 15377),
#     (154, 15506),
#     (155, 15666),
#     (156, 15866),
#     (157, 16094),
#     (158, 16293),
#     (159, 16554),
#     (160, 16778),
#     (161, 17004),
#     (162, 17203),
#     (163, 17465),
#     (164, 17695),
#     (165, 17833),
#     (166, 18004),
#     (167, 18218),
# ]
#
# cyclic_pattern_delta_1 = []
#
# for i in range(1, len(cyclic_pattern), 1):
#     c1, v1 = cyclic_pattern[i - 1]
#     c2, v2 = cyclic_pattern[i]
#     cyclic_pattern_delta_1.append(v2 - v1)
#
# # print(cyclic_pattern_delta_1)
#
#
# cyclic_pattern_delta_2 = []
#
# for i in range(1, len(cyclic_pattern_delta_1), 1):
#     v1 = cyclic_pattern_delta_1[i - 1]
#     v2 = cyclic_pattern_delta_1[i]
#     cyclic_pattern_delta_2.append(v2 - v1)
#
# # print(cyclic_pattern_delta_2)
#
#
# cyclic_pattern_delta_3 = []
#
# for i in range(1, len(cyclic_pattern_delta_2), 1):
#     v1 = cyclic_pattern_delta_2[i - 1]
#     v2 = cyclic_pattern_delta_2[i]
#     cyclic_pattern_delta_3.append(v2 - v1)
#
# # print(cyclic_pattern_delta_3)
#
# cyclic_pattern_delta_4 = []
#
# # print(cyclic_pattern_delta_3)
#
# for i in range(11, len(cyclic_pattern_delta_3), 1):
#     v1 = cyclic_pattern_delta_3[i - 11]
#     v2 = cyclic_pattern_delta_3[i]
#     cyclic_pattern_delta_4.append(v2 - v1)
#
# # print(cyclic_pattern_delta_4)
#
# # for i in range(0, len(cyclic_pattern_delta_4), 11):
# #    print(cyclic_pattern_delta_4[i : i + 11])
#
# cyclic_pattern_delta_5 = []
# for i in range(22, len(cyclic_pattern), 11):
#     v1 = [v for c, v in cyclic_pattern[i - 22 : i - 11]]
#     v2 = [v for c, v in cyclic_pattern[i - 11 :]]
#     vr = [v2[ii] - v1[ii] for ii in range(11)]
#     # print(vr)
#     cyclic_pattern_delta_5.append(vr)
#
#
# # print(cyclic_pattern_delta_5)
#
# cyclic_pattern_delta_6 = []
# for i in range(1, len(cyclic_pattern_delta_5)):
#     for v1, v2 in zip(cyclic_pattern_delta_5[i - 1], cyclic_pattern_delta_5[i]):
#         cyclic_pattern_delta_6.append(v2 - v1)
#
# # print(cyclic_pattern_delta_6)
#
# # print(cyclic_pattern_delta_4[-11:])
# # print(cyclic_pattern_delta_4[-22:-11])
#
#
# cyclic_ranges = []
# for i in range(22, len(cyclic_pattern), 11):
#     v1 = [v for c, v in cyclic_pattern[i - 22 : i - 11]]
#     v2 = [v for c, v in cyclic_pattern[i - 11 : i or None]]
#     vr = [v2[ii] - v1[ii] for ii in range(11)]
#     # print(v1)
#     # print(v2)
#     # print("---")
#     # print(vr)
#     # cyclic_ranges.append(vr)
#     # print(max(Ranges(*v1) - min(Ranges(*v1))))
#     # print(max(Ranges(*v2) - min(Ranges(*v1))))
#     # print(max(Ranges(*v2) - min(Ranges(*v2))))
#     # print("---")
#     # cyclic_ranges(Ranges(*v1))
#
#
# async def run() -> int:
#     result = 0
#
#     matrix = values.matrix.options(infinite_x=True, infinite_y=True)
#     pos = start_pos = matrix.position("S")[0]
#     matrix = matrix.replace("S", ".")
#     possible_positions = set(matrix.position("."))
#     width = matrix.width
#     height = matrix.height
#     max_steps = 5000
#
#     result_per_step = []
#
#     queue = {(start_pos)}
#     visited = set()
#     current = 0
#     analysis_print = True
#     predicted_series = []
#     predicted_series_ = []
#     add_to_series = []
#     while True:
#         visited = set()
#         while queue:
#             pos = queue.pop()
#
#             # visited.add((pos, steps))
#             # visited.add(pos)
#
#             # if steps >= max_steps:
#             #    continue
#             for mod in ((0, 1), (1, 0), (0, -1), (-1, 0)):
#                 if not ((not mod[0] or not mod[1]) and mod != (0, 0)):
#                     continue
#                 pos_ = tuple_add(pos, mod)
#                 # if pos_[0] < 0 or pos_[0] >= matrix.width or pos_[1] < 0 or pos_[1] >= matrix.height:
#                 #     continue
#                 normalized_pos = (pos_[0] % width, pos_[1] % height)
#                 if normalized_pos not in possible_positions:
#                     continue
#                 if pos_ != normalized_pos:
#                     return
#                 # if matrix[pos_] == "#":
#                 #    print("ERROR", pos_)
#                 #    continue
#                 # key = (pos_, steps + 1)
#                 key = pos_
#                 if key in visited:
#                     continue
#                 visited.add(key)
#                 # queue.add(key)
#         queue = visited
#
#         # visited_in_matrix = {
#         #     pos_
#         #     for pos_, steps_ in visited
#         #     if steps_ == steps
#         #     and (pos_[0] >= 0 and pos_[0] < matrix.width and pos_[1] >= 0 and pos_[1] < matrix.height)
#         # }
#         # if len(visited_in_matrix) == matrix.count("."):
#         #     print("steps", steps)
#         #     print("len(visited_in_matrix)", len(visited_in_matrix))
#         #     print('matrix.count(".")', matrix.count("."))
#         #
#         #     result = 0
#         #     for pos_, steps_ in visited:
#         #         if steps_ == steps:
#         #             result += 1
#         #     # return result
#         #     # break
#
#         if current + 1 >= max_steps:
#             break
#         current += 1
#
#         result = 0
#         # for pos_, steps_ in visited:
#         # for pos_ in visited:
#         result = len(visited)
#
#         result_per_step.append(result)
#         possibly_cyclic_n = []
#
#         if True:
#             if predicted_series:
#                 predicted_result = predicted_series.pop(0)
#                 print("---")
#                 print("current:", current)
#                 print("result:", result)
#                 print("predicted_result:", predicted_result)
#                 print("---")
#                 if predicted_result == result:
#                     print("success: predicted result matches actual result!")
#                     if not predicted_series and predicted_series_:
#                         # skip_steps = ((max_steps - current) // len(predicted_series_)) * len(predicted_series_)
#                         # print("skipping steps:", skip_steps)
#
#                         while current < max_steps:
#                             predicted_series = add_to_series[-1]
#                             for i in range(1, len(add_to_series)):
#                                 # result = functools.reduce(lambda value, el: value + 162 * el, range(0, skip_steps), result)
#                                 # add_per_step = sum(add_to_series[i])
#                                 print(f"add_to_series[{i}] (current):", add_to_series[i])
#                                 add_to_series[i] = [v1 + v2 for v1, v2 in zip(add_to_series[i], add_to_series[i - 1])]
#                                 print(f"add_to_series[{i}] (updated):", add_to_series[i])
#                             predicted_series = add_to_series[-1][:]
#                             print("predicted next values:", predicted_series)
#                             if current + len(predicted_series) < max_steps:
#                                 result += sum(predicted_series)
#                                 current += len(predicted_series)
#                             else:
#                                 result = predicted_series[max_steps - current - 1]
#                                 current = max_steps
#
#                         # result = functools.reduce(
#                         #     lambda value, el: value + el * add_per_step // len(add_to_series[i]),
#                         #     range(0, skip_steps),
#                         #     1,
#                         # )
#
#                         # result = functools.reduce(
#                         #     lambda value, el: value + (el // len(add_to_series[i])) * add_per_step // 11,
#                         #     range(current - 1, skip_steps + current, len(add_to_series[i])),
#                         #     result,
#                         # )
#
#                         # result = functools.reduce(
#                         #     lambda value, el: value + el * add_per_step,
#                         #     range(0, skip_steps, len(add_to_series[i])),
#                         #     0,
#                         # )
#
#                         # predicted_series_.append(
#                         #     [v1 + v2 for v1, v2 in zip(predicted_series_[-1], add_to_series[i])]
#                         # )
#
#                         # old_result = result_per_step[-len(predicted_series_)]
#                         # diff = result - old_result
#                         # result = result + diff * skip_steps
#                         # current += skip_steps
#                         print("---")
#                         print("current:", current)
#                         print("result:", result)
#                         print("---")
#                         # breakpoint()
#                         # return result
#                     continue
#
#                 print("failure: predicted result does not match actual result!")
#                 predicted_result = []
#                 predicted_series_ = []
#                 add_to_series = []
#
#             if current > 70:
#                 analysis_1 = [v2 - v1 for v1, v2 in zip(result_per_step, result_per_step[1:])]
#                 analysis_2 = [v2 - v1 for v1, v2 in zip(analysis_1, analysis_1[1:])]
#                 analysis_3 = [v2 - v1 for v1, v2 in zip(analysis_2, analysis_2[1:])]
#                 analysis_4 = [v2 - v1 for v1, v2 in zip(analysis_3, analysis_3[1:])]
#                 analysis_5 = [v2 - v1 for v1, v2 in zip(analysis_4, analysis_4[1:])]
#                 analysis_6 = [v2 - v1 for v1, v2 in zip(analysis_5, analysis_5[1:])]
#
#                 for analysis_ in (
#                     analysis_1,
#                     analysis_2,
#                     analysis_3,
#                     analysis_4,
#                     analysis_5,
#                     analysis_6,
#                 ):
#                     for n in range(2, len(analysis_) // 2):
#                         analysis_range = [v2 - v1 for v2, v1 in zip(analysis_[-n * 4 :], analysis_[-n * 4 :][n::])]
#                         # if analysis_range[-n * 2 : -n] == analysis_range[-n:]:
#                         #     print("possible cyclic n-value:", n)
#                         #     possibly_cyclic_n.append(n)
#                         for nn in range(0, len(analysis_range) - n * 2):
#                             range_1 = analysis_range[nn : nn + n]
#                             range_2 = analysis_range[nn + n : nn + n * 2]
#                             if range_1 == range_2:
#                                 if analysis_print:
#                                     print("possible cyclic n-value:", n)
#                                     print("range_1:", range_1, range(nn, nn + n))
#                                     print("range_2:", range_2, range(nn + n, nn + n * 2))
#                                     print("series length:", len(analysis_range))
#                                     print("")
#                                     print(analysis_)
#                                     print(analysis_range)
#                                 possibly_cyclic_n.append(n)
#                                 # possibly_cyclic_n.append(n * 2)
#                             # print(
#                             #     analysis_range[-n * 2 : -n],
#                             #     analysis_range[-n:],
#                             # )
#
#                 for n, count in Counter(possibly_cyclic_n).most_common():
#                     if count > 1:
#                         source = sorted([result_per_step[-n * i : (-n * (i - 1)) or None] for i in range(1, 7)])
#                         source = [v for v in source if len(v) == n]
#                         depth = 0
#                         source_depth = [source]
#
#                         if len(source) > 1:
#                             analysis_print = False
#                             print("analysis of probable cyclic n-value:", n)
#
#                             print(f"--- depth 0 ---")
#                             for i, range_ in enumerate(source, start=1):
#                                 print(f"range_{i}:", range_)
#
#                         while len(source) > 1:
#                             depth += 1
#                             ranges_ = []
#                             for range_1, range_2 in zip(source, source[1:]):
#                                 range_ = [v2 - v1 for v1, v2 in zip(range_1, range_2)]
#                                 ranges_.append(range_)
#                             source_depth.append(ranges_)
#
#                             print(f"--- depth {depth} ---")
#
#                             for i, range_ in enumerate(ranges_, start=1):
#                                 print(f"range_{i}:", range_)
#
#                             if len(ranges_) > 1 and ranges_.count(ranges_[0]) == len(ranges_):
#                                 series = ranges_[-1]
#                                 add_to_series = [series]
#                                 for depth_ in range(depth - 1, -1, -1):
#                                     series = [v1 + v2 for v1, v2 in zip(source_depth[depth_][-1], series)]
#                                     # if depth_ > 0:
#                                     add_to_series.append(series[:])
#                                 predicted_series = series
#                                 predicted_series_ = series[:]
#                                 print("success: cyclic pattern found!")
#                                 print("predicted next values:", predicted_series)
#                                 break
#
#                             source = ranges_[:]
#
#                         #     range_ = source[-n * depth : -n * (depth - 1)]
#                         #
#                         #     range_1 = result_per_step[-n * 4 : -n * 3]
#                         #     range_2 = result_per_step[-n * 3 : -n * 2]
#                         #     range_3 = result_per_step[-n * 2 : -n]
#                         #     range_4 = result_per_step[-n:]
#                         # ranges_ = [range_1, range_2, range_3, range_4]
#                         # print("probable cyclic n-value:", n)
#                         # print("range_1:", range_1, "match:")
#                         # print("range_2:", range_2, "match:")
#                         # print("range_3:", range_3, "match:")
#                         # print("range_4:", range_4, "match:")
#
#                         # delta_1 = [v2 - v1 for v1, v2 in zip(range_1, range_2)]
#                         # delta_2 = [v2 - v1 for v1, v2 in zip(range_2, range_3)]
#                         # delta_3 = [v2 - v1 for v1, v2 in zip(range_3, range_4)]
#                         # deltas_ = [delta_1, delta_2, delta_3]
#                         # print("delta_1:", delta_1, "match:", deltas_.count(delta_1))
#                         # print("delta_2:", delta_2, "match:", deltas_.count(delta_2))
#                         # print("delta_3:", delta_3, "match:", deltas_.count(delta_3))
#
#                         continue
#
#             # print("---")
#             # print("analysis_1", analysis_1)
#             # print("analysis_2", analysis_2)
#             # print("analysis_3", analysis_3)
#             # print("analysis_4", analysis_4)
#             # print("analysis_5", analysis_4)
#             # print("---")
#             # for v1, v2 in zip(result_per_step, result_per_step[1:]:
#
#             print("---")
#             print("current:", current)
#             print("result:", result)
#             print("possibly_cyclic_n:", Counter(possibly_cyclic_n).most_common())
#             print("---")
#
#             matrix_ = Matrix(matrix)
#             for pos in visited:
#                 if pos[0] >= 0 and pos[0] < matrix_.width and pos[1] >= 0 and pos[1] < matrix_.height:
#                     matrix_[pos] = "O"
#                 # if steps == current:
#                 # result += 1
#
#             print(matrix_)
#
#         if False:
#             result = 0
#             matrix_ = Matrix(matrix)
#             for pos_, steps_ in visited:
#                 if steps_ == current - 1 and (
#                     pos_[0] >= 0 and pos_[0] < matrix_.width and pos_[1] >= 0 and pos_[1] < matrix_.height
#                 ):
#                     matrix_[pos_] = "O"
#                 if steps_ == current - 1:
#                     result += 1
#             print("---")
#             print("current:", current)
#             print("in matrix (O):", matrix_.count("O"))
#             print("in matrix (.):", matrix_.count("."))
#             print("result:", result)
#             print(matrix_)
#             print("---")
#
#     # result = len(visited)
#     for pos in visited:
#         if pos[0] >= 0 and pos[0] < matrix.width and pos[1] >= 0 and pos[1] < matrix.height:
#             matrix[pos] = "O"
#         # if steps == current:
#         # result += 1
#
#     print(matrix)
#     values.matrix_count = matrix.count("O")
#     return result
#
#     for row in values:
#         pass
#
#     return result
#
#
# [values.year]            (number)  2023
# [values.day]             (number)  0
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day0/input
#
# Result: 609585229256084
