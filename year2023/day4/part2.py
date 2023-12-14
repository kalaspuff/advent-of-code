from values import values


async def run() -> int:
    result = 0
    originals: list[tuple[int, int]] = []

    for index, (_, winning_numbers, my_numbers) in enumerate(values.split_values([":", "|"])):
        matches = len(set(winning_numbers.ints()) & set(my_numbers.ints()))
        originals.append((index, matches))

    cards = originals[:]
    while cards:
        index, matches = cards.pop()
        result += 1
        cards.extend(originals[index + 1 : index + 1 + matches])

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  4
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day4/input
#
# Result: 8570000
