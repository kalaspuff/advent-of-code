from helpers import split_to_dict
from values import values


async def run():
    passports = [split_to_dict(rows, " ", ":") for rows in values.grouped_rows()]

    required_fields = {
        "byr",  # (Birth Year)
        "iyr",  # (Issue Year)
        "eyr",  # (Expiration Year)
        "hgt",  # (Height)
        "hcl",  # (Hair Color)
        "ecl",  # (Eye Color)
        "pid",  # (Passport ID)
    }

    valid_passports = [passport for passport in passports if not required_fields - set(passport.keys())]
    return len(valid_passports)


# [values.year]            (number)  2020
# [values.day]             (number)  4
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2020/day4/input
#
# Result: 192
