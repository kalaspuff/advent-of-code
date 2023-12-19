from values import values


class Workflow:
    def __init__(self, name: str, rules: tuple[tuple[str, ...], ...], fallback: str):
        self.name = name
        self.rules = tuple(((c[0], c[1], int(c[2:])), next_) for c, next_ in rules)
        self.fallback = fallback

    def __repr__(self):
        return f'Workflow("{self.name}", rules={self.rules}, fallback="{self.fallback}")'


def is_part_accepted(workflows: dict[str, Workflow], workflow: Workflow, part: dict[str, int]) -> bool:
    while True:
        for (attribute, op, threshold), next_ in workflow.rules:
            if (op == ">" and part[attribute] > threshold) or (op == "<" and part[attribute] < threshold):
                if next_ not in workflows:
                    return next_ == "A"
                workflow = workflows[next_]
                break
        else:
            next_ = workflow.fallback
            if next_ not in workflows:
                return next_ == "A"
            workflow = workflows[next_]


async def run() -> int:
    result = 0
    workflows = {}
    parts = []

    workflows_input, parts_input = values.split_sections("\n\n")

    for name, rules_str in workflows_input.match_rows("([a-z]+)[{]([^}]*)[}]"):
        rules: tuple[tuple[str, ...], ...] = tuple(tuple(rule.split(":", 1)) for rule in rules_str.split(","))
        workflows[name] = Workflow(name, rules[0:-1], rules[-1][0])

    for ratings in [row.strip("{}").split(",") for row in parts_input]:
        part = {rating.split("=")[0]: int(rating.split("=")[1]) for rating in ratings}
        parts.append(part)

    for part in parts:
        if is_part_accepted(workflows, workflows["in"], part):
            result += sum(part.values())

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  19
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2023/day19/input
#
# Result: 325952
