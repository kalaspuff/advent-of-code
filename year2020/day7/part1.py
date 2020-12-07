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

    def can_hold_bag(this_bag_type, test_bag_type):
        contents = bag_rules[test_bag_type]
        if not contents:
            return False
        if this_bag_type in contents:
            return True
        return any([can_hold_bag(this_bag_type, bag_type) for bag_type in contents.keys()])

    my_bag_type = "shiny gold"
    for bag_type in bag_rules.keys():
        if can_hold_bag(my_bag_type, bag_type):
            values.counter += 1

    return values.counter


# [values.year]            (number)  2020
# [values.day]             (number)  7
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2020/day7/input
# [values.counter]         (number)  235
#
# Result: 235
