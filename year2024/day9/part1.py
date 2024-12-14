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

    def get_first_free_space(self, start: int) -> int:
        return self.blocks.index(FreeSpace(), start)

    def compress(self) -> None:
        first_free = self.get_first_free_space(0)

        for i in reversed(range(len(self.blocks))):
            if first_free > i:
                break

            if isinstance(self[i], File):
                self[first_free] = self.free(i)
                first_free = self.get_first_free_space(first_free)

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
    disk.compress()

    return disk.checksum


# [values.year]            (number)  2024
# [values.day]             (number)  9
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2024/day9/input
#
# Result: 6337367222422
