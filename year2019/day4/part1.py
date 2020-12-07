from values import values


async def run():
    from_, to_ = values.match(r"^([0-9]+)-([0-9]+)$", (int, int))
    for password in range(from_, to_ + 1):
        str_password = str(password)
        list_password = list(map(int, list(str_password)))

        if len(list_password) != 6:
            continue
        if not any([f"{d}{d}" in str_password for d in range(0, 10)]):
            continue
        if not all([True if i == 0 or list_password[i - 1] <= d else False for i, d in enumerate(list_password)]):
            continue

        values.counter += 1

    return values.counter


# [values.year]            (number)  2019
# [values.day]             (number)  4
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2019/day4/input
# [values.counter]         (number)  1716
#
# Result: 1716
