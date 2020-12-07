import re

from values import values


async def run():
    bag_rules = {}
    for bag_type, contents_str in values.match_rows(r"^([a-z]+ [a-z]+) bags contain (.*)[.]$"):
        contents = {}
        if contents_str != "no other bags":
            for c in contents_str.split(", "):
                m = re.match(r"^([0-9]+) ([a-z]+ [a-z]+) bags?$", c)
                contents[m.group(2)] = int(m.group(1))
        bag_rules[bag_type] = contents

    my_bag_type = "shiny gold"
    bags_to_count = [my_bag_type]
    while bags_to_count:
        current_bag_type = bags_to_count.pop()
        for bag_type, bag_count in bag_rules[current_bag_type].items():
            values.counter += bag_count
            for _ in range(0, bag_count):
                bags_to_count.append(bag_type)

    return values.counter


# [values.year]            (number)  2020
# [values.day]             (number)  7
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2020/day7/input
# [values.counter]         (number)  158493
#
# Result: 158493
