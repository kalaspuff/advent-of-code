import re

from values import values


async def run():
    stacks = []

    x = 0
    for x, row in enumerate(values.rows):
        if re.match(r"^[0-9 ]*$", row):
            break

        crates = [row[i+1] for i in range(0, len(row), 4)]
        for i, c in enumerate(crates):
            if len(stacks) <= i:
                stacks.append([])
            if c != " ":
                stacks[i].insert(0, c)

    for row in values.rows[x+2:]:
        count, from_stack, to_stack = map(int, re.match(r"^move (\d+) from (\d+) to (\d+)", row).groups())
        from_stack -= 1
        to_stack -= 1

        stacks[to_stack] = stacks[to_stack] + stacks[from_stack][-count:]
        stacks[from_stack] = stacks[from_stack][0:-count]

    return "".join([s[-1] for s in stacks])


# [values.year]            (number)  2022
# [values.day]             (number)  5
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day5/input
#
# Result: MGDMPSZTM
