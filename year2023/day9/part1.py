from helpers import pairwise
from values import values


async def run() -> int:
    result = 0

    for row in values.findall_int():
        sequences = [list(row)]

        while any(sequences[-1]):
            sequence = [int.__rsub__(*pair) for pair in pairwise(sequences[-1])]
            sequences.append(sequence)

        result += sum(sequence[-1] for sequence in sequences)

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  9
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day9/input
#
# Result: 1934898178
