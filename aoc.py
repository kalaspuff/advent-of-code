# note: code may have been written in a rush, here be dragons and lots of bad patterns to avoid.

import asyncio
import decimal
import importlib
import importlib.util
import itertools
import math
import os
import pathlib
import sys
import time
import typing

import helpers
from values import Values, values

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
if input_filename.startswith(("./", "../")):
    input_filename_fullpath = f"{cwd}/{input_filename}"
    input_filename = input_filename_fullpath.rsplit("/", 1)[1]
elif input_filename.startswith("/"):
    input_filename_fullpath = input_filename
    input_filename = input_filename_fullpath.rsplit("/", 1)[1]
elif "/" not in input_filename:
    input_filename_fullpath = f"{day_path}/{input_filename}"
elif input_filename.startswith(f"year{year}/day{day}/"):
    input_filename = input_filename.replace(f"year{year}/day{day}/", "", 1)
    input_filename_fullpath = f"{day_path}/{input_filename}"
else:
    input_filename_fullpath = f"{cwd}/{input_filename}"
    input_filename = input_filename_fullpath.rsplit("/", 1)[1]

input_ = ""
try:
    with open(input_filename_fullpath) as f:
        input_ = f.read()
except Exception:
    print("warning: cannot read puzzle input from file")
    raise

path_prefix = os.path.commonprefix([os.path.realpath(python_filepath), cwd])
if os.path.realpath(input_filename_fullpath).startswith(path_prefix):
    input_filename_fullpath = os.path.realpath(input_filename_fullpath)
    relative_filename = "./" + input_filename_fullpath[len(path_prefix) :].lstrip("/")
else:
    relative_filename = os.path.realpath(input_filename_fullpath)

values.input_ = input_.rstrip()
values._rows = values.input_.split("\n")
values.year = year
values.day = day
values.part = part
values.input_filename = relative_filename
values.result = []
values.counter = 0


async def _async() -> None:
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

    # inject values into module (it's messy, but with quicker access we some seconds of typing)
    if getattr(module_import, "values", None) is None:
        setattr(module_import, "values", values)
    for name in ("rows", "lines"):
        if getattr(module_import, name, None) is None:
            setattr(module_import, name, values.rows)
    for name in ("matrix", "grid"):
        if getattr(module_import, name, None) is None:
            setattr(module_import, name, values.matrix)
    for name in ("input", "raw", "data", "raw_input", "raw_data"):
        if getattr(module_import, name, None) is None:
            setattr(module_import, name, values.input_)
    for name in ("Values",):
        if getattr(module_import, name, None) is None:
            setattr(module_import, name, Values)
    for name in ("is_example", "example"):
        if getattr(module_import, name, None) is None:
            setattr(module_import, name, "input" not in values.input_basename)

    # inject helper functions into module
    for name in helpers.__dict__:
        if not name.startswith("_") and name not in module_import.__dict__:
            setattr(module_import, name, getattr(helpers, name))

    # inject nice-to-have modules
    for module in (math, itertools, helpers):
        name = module.__name__
        if not name.startswith("_") and name not in module_import.__dict__:
            setattr(module_import, name, module)

    # inject types into module
    for name in (
        "Dict",
        "List",
        "Set",
        "Tuple",
        "Optional",
        "Union",
        "Any",
        "Callable",
        "Iterable",
        "Type",
        "Literal",
    ):
        if not name.startswith("_") and name not in module_import.__dict__:
            setattr(module_import, name, getattr(typing, name))

    getattr(spec.loader, "exec_module")(module_import)  # noqa: B009

    result_large_output = False
    start_time = time.time()

    try:
        result = await getattr(module_import, "run")()  # noqa: B009
    except Exception as exc:
        result = exc

    values.elapsed_time = time.time() - start_time
    grouped_attrs = {"year", "day", "part", "input_filename", "elapsed_time"}

    if result is None and getattr(values, "result", None):
        result = getattr(values, "result", None)

    if result is None and getattr(values, "counter", None):
        result = getattr(values, "counter", None)

    if "result" in values.attrs:
        attr_value = values.result
        values.attrs.remove("result")
        if attr_value and result != attr_value:
            values.attrs.append("result")

    if isinstance(result, str):
        result = result.strip()

    if "_result" in values.attrs:
        if values._result and result and values._result != result:
            print("WARNING: _result already set in values.attrs")
            print("WARNING: _result will be overwritten")
            print("PREVIOUS _result:")
            print(values._result)
            print("---")
        values.attrs.remove("_result")

    if result is not None:
        values._result = result
        values.attrs.append("_result")

    for key_ in values.attrs:
        key = key_

        if key in ("input",):
            continue

        v = getattr(values, key, None)

        type_ = type(v).__name__
        if isinstance(v, decimal.Decimal):
            type_ = "number"
        if isinstance(v, (Exception, BaseException)):
            type_ = "error"
            v = "[uncaught exception]"
        if isinstance(v, bool):
            v = "true" if v else "false"

        category = "values"
        emoji = "❄️ "

        match key:
            case "year" | "day":
                category = "challenge"
                emoji = "🗓️ "
                type_ = "number"
            case "part":
                category = "challenge"
                emoji = "🧦"
                type_ = "number"
            case "input_filename":
                category = "puzzle"
                key = "input.filename"
                type_ = "path"
                emoji = "💾"
                v = f"{v} ({len(values.input_)} bytes)"
            case "elapsed_time":
                category = "process"
                key = "time.elapsed"
                type_ = "seconds"
                emoji = "⏱️ "
                v = f"{v:.6f}"
            case "_result":
                category = "output"
                key = "result"
                emoji = "🎁"
                try:
                    if bool("\n" in str(v) or len(str(v)) > 40):
                        result_large_output = True
                        v = "[large result]"
                except Exception:
                    result_large_output = True

        type_str = f"{type_}"
        type_str = f"{type_str:9s}"

        key_str = f"{category}.{key}"
        key_str = f"{key_str:24s}"

        if not grouped_attrs:
            grouped_attrs.add(key_)
            print("---")
        elif key_ in grouped_attrs:
            grouped_attrs.remove(key_)

        try:
            print(f"{key_str} {emoji} {type_str} {v}")
        except Exception:
            print(f"{key_str} {emoji} {type_str} [cannot be coerced to str]")

    try:
        if isinstance(result, list) and all(isinstance(row, (str)) for row in result):
            result = "\n".join(result)
            result_large_output = True
    except Exception:
        pass

    if result_large_output:
        print("")
        try:
            print(result)
        except Exception as exc:
            print("result cannot be coerced to str")
            result = exc

    if isinstance(result, Exception):
        import traceback

        frames = []
        tb_back = None
        tb = result.__traceback__

        while tb:
            module_name = tb.tb_frame.f_globals.get("__name__", "") if tb.tb_frame and tb.tb_frame.f_globals else ""
            frames.append((tb, module_name))
            if module_name not in ("cli", "aoc"):
                tb_back = tb
            tb = tb.tb_next

        if tb_back:
            for tb, module_name in reversed(frames):
                if tb_back:
                    if tb is not tb_back:
                        continue
                    tb_back = None

                if tb.tb_next and module_name in ("cli", "aoc"):
                    result.with_traceback(tb.tb_next)
                    break

        print("")
        traceback.print_exception(type(result), result, result.__traceback__, None)

    if values.input_ == "":
        print("")
        print("warning: puzzle input was missing or empty")

    if isinstance(result, (Exception, BaseException)):
        sys.exit(1)


asyncio.run(_async())
