from values import values
from year2022.computer import Computer, Filesystem


async def run():
    cpu = Computer("The Device", filesystems=[Filesystem("root", mount="/", total_space=70000000)])
    cpu.set_state_from_terminal_log(values.input_)

    # from year2022.computer import Command, Interface
    # Interface(cpu).execute(Command(cmdline="info"))
    # Interface(cpu).connect()

    return sum([dir.size for dir in cpu.get_all_dirs() if dir.size <= 100000])


# [values.year]            (number)  2022
# [values.day]             (number)  7
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day7/input
#
# Result: 1543140
