from values import Values, values


class File:
    def __init__(self, id_: int, length: int):
        self.id = id_
        self.length = length


class FreeSpace:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance


class Disk:
    def __init__(self, disk_map: str | Values):
        free_space = FreeSpace()
        self.blocks: list[File | FreeSpace] = []

        is_file = True
        id_ = 0
        for c in Values(disk_map).flatten().digits():
            if is_file:
                file = File(id_, c)
                id_ += 1
                for _ in range(c):
                    self.blocks.append(file)
            else:
                for _ in range(int(c)):
                    self.blocks.append(free_space)
            is_file = not is_file

    def __getitem__(self, block: int) -> File | FreeSpace:
        return self.blocks[block]

    def __setitem__(self, block: int, value: File | FreeSpace) -> None:
        self.blocks[block] = value

    def pop(self, block: int) -> File | FreeSpace:
        return self.blocks.pop(block)

    def free(self, block: int) -> File | FreeSpace:
        value = self.blocks[block]
        self.blocks[block] = FreeSpace()
        return value

    def get_first_free_space(self, start: int, length: int = 1) -> int:
        free_space = FreeSpace()

        while True:
            idx = self.blocks.index(free_space, start)
            for i in range(idx + 1, idx + length):
                if i >= len(self.blocks):
                    raise ValueError("no free space")
                if self[i] is not free_space:
                    start = i + 1
                    break
            else:
                return idx

    def defrag(self) -> None:
        first_free = self.get_first_free_space(0)

        for i in reversed(range(len(self.blocks))):
            file = self[i]
            if isinstance(file, File):
                file_start = i - (file.length - 1)
                file_end = i
                try:
                    free_idx = self.get_first_free_space(first_free, file.length)
                    if free_idx > file_start:
                        continue
                    for j in range(file_start, file_end + 1):
                        self.free(j)
                    for j in range(file.length):
                        self[free_idx + j] = file

                    first_free = self.get_first_free_space(first_free)
                except ValueError:
                    pass

    def __str__(self) -> str:
        result = ""
        for block in self.blocks:
            if isinstance(block, File):
                result += str(block.id)[0]
            else:
                result += "."
        return result

    @property
    def checksum(self) -> int:
        return sum(i * block.id for i, block in enumerate(self.blocks) if isinstance(block, File))


async def run() -> int:
    disk = Disk(values)
    disk.defrag()

    return disk.checksum


# [values.year]            (number)  2024
# [values.day]             (number)  9
# [values.part]            (number)  2
# [values.input_filename]  (str)     ./year2024/day9/input
#
# Result: 6361380647183
