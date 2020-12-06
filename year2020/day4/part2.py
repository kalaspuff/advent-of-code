import re

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

    passports_to_validate = [passport for passport in passports if not required_fields - set(passport.keys())]
    for passport in passports_to_validate:
        if not 1920 <= int(passport["byr"]) <= 2002:
            continue
        if not 2010 <= int(passport["iyr"]) <= 2020:
            continue
        if not 2020 <= int(passport["eyr"]) <= 2030:
            continue
        if not passport["hgt"].endswith("cm") and not passport["hgt"].endswith("in"):
            continue
        if passport["hgt"].endswith("cm") and not 150 <= int(passport["hgt"][:-2]) <= 193:
            continue
        if passport["hgt"].endswith("in") and not 59 <= int(passport["hgt"][:-2]) <= 76:
            continue
        if not re.match(r"^#[0-9a-f]{6}$", passport["hcl"]):
            continue
        if passport["ecl"] not in ("amb", "blu", "brn", "gry", "grn", "hzl", "oth"):
            continue
        if not re.match(r"^[0-9]{9}$", passport["pid"]):
            continue

        values.counter += 1

    return values.counter


# [values.year]            (number)  2020
# [values.day]             (number)  4
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2020/day4/input
# [values.counter]         (number)  101
#
# Result: 101
