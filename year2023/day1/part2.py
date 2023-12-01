from values import values


async def run():
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

    for row in values.rows:
        digits = []

        for i in range(len(row) + 1):
            row_ = row[0:i]
            for word, num in word_to_num.items():
                if word in row_ or num in row_:
                    digits.append(num)
                    break
            if digits:
                break

        for i in range(len(row) + 1):
            row_ = row[-i - 1 :]
            for word, num in word_to_num.items():
                if word in row_ or num in row_:
                    digits.append(num)
                    break
            if len(digits) == 2:
                break

        result += int(str(digits[0]) + str(digits[-1]))

    return result


# [values.year]            (number)  2023
# [values.day]             (number)  1
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2023/day1/input
#
# Result: 55652
