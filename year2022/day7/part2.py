from values import values
from year2022.computer import Computer, Filesystem


async def run():
    cpu = Computer("the device", filesystems=[Filesystem("root", mount="/", total_space=70000000)])
    cpu.set_state_from_terminal_log(values.input_)

    return min([dir.size for dir in cpu.get_all_dirs() if dir.size >= 30000000 - cpu.filesystems["root"].free_space])


# [values.year]            (number)  2022
# [values.day]             (number)  7
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2022/day7/input
#
# Result: 1117448
