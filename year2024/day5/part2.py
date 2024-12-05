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
            continue

        ordered_pages: list[int] = []

        while len(ordered_pages) < len(pages):
            for page in (p for p in pages if p not in ordered_pages):
                for page_ in (p for p in pages if p not in ordered_pages):
                    if page in rules[page_]:
                        break
                else:
                    ordered_pages.append(page)

        result += ordered_pages[len(ordered_pages) // 2]

    return result


# [values.year]            (number)  2024
# [values.day]             (number)  5
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day5/input
#
# Result: 5502
