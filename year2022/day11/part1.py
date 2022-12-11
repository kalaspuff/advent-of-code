import math
import re

from values import values


class Monkey:
    def __init__(self, data, monkeys):
        self.data = data
        self.monkeys = monkeys
        self.items_inspected = 0

        items = []
        for row in self.data:
            m = re.match(r"^  Starting items: ([0-9, ]*)$", row)
            if m:
                items = list(map(int, m.group(1).split(", ", )))

        self.items = items or []

    def inspect_item(self, item_index):
        self.items_inspected += 1
        for row in self.data:
            m = re.match(r"^  Operation: new = old [*] ([0-9]+)$", row)
            if m:
                self.items[item_index] = self.items[item_index] * int(m.group(1))
                print(f"    Worry level is multiplied by {int(m.group(1))} to {self.items[item_index]}.")
            m = re.match(r"^  Operation: new = ([0-9]+) [*] old$", row)
            if m:
                self.items[item_index] = self.items[item_index] * int(m.group(1))
                print(f"    Worry level is multiplied by {int(m.group(1))} to {self.items[item_index]}.")
            m = re.match(r"^  Operation: new = old [*] old$", row)
            if m:
                self.items[item_index] = self.items[item_index] * self.items[item_index]
                print(f"    Worry level is multiplied by itself to {self.items[item_index]}.")

            m = re.match(r"^  Operation: new = old [+] ([0-9]+)$", row)
            if m:
                self.items[item_index] = self.items[item_index] + int(m.group(1))
                print(f"    Worry level increases by {int(m.group(1))} to {self.items[item_index]}.")
            m = re.match(r"^  Operation: new = ([0-9]+) [+] old$", row)
            if m:
                self.items[item_index] = self.items[item_index] + int(m.group(1))
                print(f"    Worry level increases by {int(m.group(1))} to {self.items[item_index]}.")
            m = re.match(r"^  Operation: new = old [+] old$", row)
            if m:
                self.items[item_index] = self.items[item_index] + self.items[item_index]
                print(f"    Worry level increases by itself to {self.items[item_index]}.")

    def bored_of_item(self, item_index):
        self.items[item_index] = self.items[item_index] // 3
        print(f"    Monkey gets bored with item. Worry level is divided by 3 to {self.items[item_index]}.")

    def throw_item(self, item_index):
        divisible = 0
        for row in self.data:
            m = re.match(r"^  Test: divisible by ([0-9]+)$", row)
            if m:
                divisible = int(m.group(1))
            m = re.match(r"^    If (true|false): throw to monkey ([0-9]+)$", row)
            if m:
                if m.group(1) == "true" and self.items[item_index] % divisible == 0:
                    print(f"    Item with worry level {self.items[item_index]} is thrown to monkey {int(m.group(2))}.")
                    self.monkeys[int(m.group(2))].items.append(self.items[item_index])
                    self.items.pop(item_index)
                    return
                elif m.group(1) == "false" and self.items[item_index] % divisible != 0:
                    print(f"    Item with worry level {self.items[item_index]} is thrown to monkey {int(m.group(2))}.")
                    self.monkeys[int(m.group(2))].items.append(self.items[item_index])
                    self.items.pop(item_index)
                    return


async def run():
    monkeys = []
    for rows in values.grouped_rows():
        monkeys.append(Monkey(rows, monkeys))

    for _ in range(20):
        for id_, monkey in enumerate(monkeys):
            if monkey.items:
                print(f"Monkey {id_}:")
                while monkey.items:
                    item_index = 0
                    print(f"  Monkey inspects an item with a worry level of {monkey.items[item_index]}.")
                    monkey.inspect_item(item_index)
                    monkey.bored_of_item(item_index)
                    monkey.throw_item(item_index)

    print("")
    for id_, monkey in enumerate(monkeys):
        print(f"Monkey {id_} inspected items {monkey.items_inspected} times.")

    return math.prod(map(lambda m: m.items_inspected, sorted(monkeys, key=lambda monkey: monkey.items_inspected, reverse=True)[0:2]))


# [values.year]            (number)  2022
# [values.day]             (number)  11
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day11/input
#
# Result: 58322
