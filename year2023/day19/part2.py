import functools

from helpers import Range
from values import values


class Workflow:
    def __init__(self, name: str, rules: tuple[tuple[str, ...], ...], fallback: str):
        self.name = name
        self.rules = tuple(((c[0], c[1], int(c[2:])), next_) for c, next_ in rules)
        self.fallback = fallback

    def __repr__(self):
        return f'Workflow("{self.name}", rules={self.rules}, fallback="{self.fallback}")'


def split_parts(workflows: dict[str, Workflow], workflow: Workflow, part: dict[str, Range]) -> list[dict[str, Range]]:
    parts: list[dict[str, Range]] = []
    while True:
        for (attribute, op, threshold), next_ in workflow.rules:
            if (op == ">" and part[attribute] > threshold) or (op == "<" and part[attribute] < threshold):
                pass
            elif op == ">" and part[attribute] >= threshold + 1:
                rest, current = part[attribute].split(threshold + 1)
                parts.append({**part, attribute: rest})
                part = {**part, attribute: current}
            elif op == "<" and part[attribute] <= threshold - 1:
                current, rest = part[attribute].split(threshold)
                parts.append({**part, attribute: rest})
                part = {**part, attribute: current}
            else:
                continue
            if next_ not in workflows:
                return [*parts, part] if next_ == "A" else parts
            workflow = workflows[next_]
            break
        else:
            next_ = workflow.fallback
            if next_ not in workflows:
                return [*parts, part] if next_ == "A" else parts
            workflow = workflows[next_]


async def run() -> int:
    result = 0
    workflows = {}
    parts = [{k: Range(start=1, end=4000) for k in "xmas"}]

    workflows_input, _ = values.split_sections("\n\n")

    for name, rules_str in workflows_input.match_rows("([a-z]+)[{]([^}]*)[}]"):
        rules: tuple[tuple[str, ...], ...] = tuple(tuple(rule.split(":", 1)) for rule in rules_str.split(","))
        workflows[name] = Workflow(name, rules[0:-1], rules[-1][0])

    while parts:
        part = parts.pop()
        parts_ = [p for p in split_parts(workflows, workflows["in"], part) if all(p.values())]
        if len(parts_) == 1 and parts_[0] == part:
            result += functools.reduce(lambda current, range_: current * len(range_), part.values(), 1)
        else:
            parts.extend(parts_)

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  19
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day19/input
#
# Result: 125744206494820
