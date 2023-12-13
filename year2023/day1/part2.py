from values import values


async def run() -> int:
    result = 0
    word_to_num = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
    }

    search_values = word_to_num.keys() | word_to_num.values()
    reversed_search_values = {word[::-1] for word in search_values}

    for row in values:
        first = row.words(search_values)[0]
        last = row.reversed().words(reversed_search_values)[0][::-1]

        digits = [int(word_to_num.get(first, first)), int(word_to_num.get(last, last))]
        result += digits[0] * 10 + digits[-1]

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day1/input
#
# Result: 55652
