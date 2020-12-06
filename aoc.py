#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import decimal
import importlib
import importlib.util
import pathlib
import sys

from values import values

if len(sys.argv) < 4:
    print("usage: python aoc.py <year> <day> <part> [puzzle input filename]")
    sys.exit(0)


year = int(sys.argv[1].replace("year-", "").replace("year_", "").replace("year", "").replace("y", ""))
day = int(sys.argv[2].replace("day-", "").replace("day_", "").replace("day", "").replace("d", ""))
part = int(
    sys.argv[3].replace("part-", "").replace("part_", "").replace("part", "").replace(".py", "").replace("p", "")
)

cwd = str(pathlib.Path(__file__).parent.absolute())
year_path = f"{cwd}/year{year}"
day_path = f"{year_path}/day{day}"

sys.path.insert(0, cwd)
sys.path.insert(0, year_path)
sys.path.insert(0, day_path)

python_filepath = f"{day_path}/part{part}.py"

input_filename = sys.argv[4] if len(sys.argv) > 4 else "input"
if input_filename.startswith("./"):
    input_filename_fullpath = f"{cwd}/{input_filename}"
    input_filename = input_filename_fullpath.rsplit("/", 1)[1]
elif input_filename.startswith("/"):
    input_filename_fullpath = input_filename
    input_filename = input_filename_fullpath.rsplit("/", 1)[1]
else:
    input_filename = input_filename.replace(f"year{year}/day{day}/", "")
    input_filename_fullpath = f"{day_path}/{input_filename}"

input_ = ""
with open(input_filename_fullpath, "r") as f:
    input_ = f.read()

input_ = input_.strip()

values.input_ = input_

values.year = year
values.day = day
values.part = part
values.input_filename = ".{}".format(input_filename_fullpath.split(cwd, 1)[1])
values.result = []
values.counter = 0


async def _async():
    try:
        spec = importlib.util.find_spec(
            ".{}".format(python_filepath.rsplit("/", 1)[1])[:-3], package=python_filepath.rsplit("/", 2)[1]
        )
    except ModuleNotFoundError:
        print(f"Error: invalid import - module not found @ {python_filepath}")
        sys.exit(1)

    if not spec:
        print("Error: invalid import")
        sys.exit(1)

    module_import = importlib.util.module_from_spec(spec)
    getattr(spec.loader, "exec_module")(module_import)

    result = await getattr(module_import, "run")()
    result_output = False

    for key in values.attrs:
        if key in ("input",):
            continue

        result_output = True
        v = getattr(values, key, None)

        if key == "result" and not v:
            continue

        key_str = f"[values.{key}]"
        key_str = f"{key_str:24s}"

        if isinstance(v, str):
            print("{} (str)     {}".format(key_str, v))
        elif isinstance(v, bool):
            print("{} (bool)    {}".format(key_str, "true" if v else "false"))
        elif isinstance(v, (int, float)):
            print("{} (number)  {}".format(key_str, v))
        elif isinstance(v, (decimal.Decimal)):
            print("{} (number)  {}".format(key_str, v))
        elif isinstance(v, (tuple)):
            print("{} (tuple)   {}".format(key_str, v))
        elif isinstance(v, (dict)):
            print("{} (dict)    {}".format(key_str, v))
        elif isinstance(v, (list)):
            print("{} (list)    {}".format(key_str, v))
        else:
            print("{} (unknown) {}".format(key_str, v))

    if result is None and getattr(values, "result", None):
        result = getattr(values, "result", None)

    if result is None and getattr(values, "counter", None):
        result = getattr(values, "counter", None)

    if result is not None:
        if result_output:
            print("")

        if result is str and "\n" in result:
            print("Result:")
            print(result)
        else:
            print(f"Result: {result}")


asyncio.run(_async())
