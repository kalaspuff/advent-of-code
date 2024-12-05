from collections import defaultdict

from values import values


async def run() -> int:
    result = 0

    rules_section, updates_section = values.split_sections("\n\n")
    rules = defaultdict(set)

    for before, after in rules_section.ints():
        rules[before].add(after)

    for pages in updates_section.ints():
        for i, page in enumerate(pages):
            for next_page in pages[i + 1 :]:
                if page in rules[next_page]:
                    break
            else:
                continue
            break
        else:
            result += pages[len(pages) // 2]

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  5
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day5/input
#
# Result: 5747
