import re
from functools import reduce


class File:
    def __init__(self, parent, name, size):
        self.parent = parent
        self.name = name
        self.size = size

    @property
    def path(self):
        return "/" + f"{self.parent.path}/{self.name}".strip("/")

    def __str__(self):
        return f"file('{self.path}', size={self.size})"


class Directory:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.dirs = {}
        self.files = {}

    def mkdir(self, name):
        if name not in self.dirs:
            self.dirs[name] = Directory(self, name)

    def add_file(self, name, size):
        if name not in self.files:
            self.files[name] = File(self, name, size)

    @property
    def size(self):
        return sum([dir.size for dir in self.dirs.values()]) + sum([file.size for file in self.files.values()])

    @property
    def path(self):
        return "/" + f"{self.parent.path}/{self.name}".strip("/")

    def __str__(self):
        return f"dir('{self.path}', size={self.size})"


class Filesystem:
    def __init__(self, name, mount, total_space):
        self.name = name
        self.mount = mount
        self.root = Directory(self, "")
        self.total_space = total_space

    @property
    def available_space(self):
        return self.total_space - self.used_space

    @property
    def used_space(self):
        return self.root.size

    @property
    def path(self):
        return self.mount

    def __str__(self):
        return f"fs('{self.name}', mount='{self.mount}', used={self.used_space}, avail={self.available_space})"


class Computer:
    def __init__(self, name, filesystems):
        self.name = name
        self.filesystems = {fs.name: fs for fs in filesystems}

    def _get_path(self, path):
        return "/" + "/".join(reduce(lambda a, b: ((a + [b]) if b != ".." else a[:-1]) if b else a, [p for p in path.split("/") if p], []))

    def get_filesystem(self, path):
        path = self._get_path(path)
        candidates = []
        for fs in self.filesystems.values():
            if path in (fs.mount, f"{fs.mount}/") or path.startswith(fs.mount.rstrip("/") + "/"):
                candidates.append((len(fs.mount), fs))
        return sorted(candidates, key=lambda x: x[0])[-1][1]

    def get_dir(self, path):
        path = self._get_path(path)
        filesystem = self.get_filesystem(path)
        fs_path = path[len(filesystem.mount):]
        dir = filesystem.root
        for p in fs_path.split("/"):
            if p:
                dir = dir.dirs[p]
        return dir

    def get_all_dirs(self):
        result = []
        for fs in sorted(self.filesystems.values()):
            dirs = [fs.root]
            while dirs:
                cwd = dirs.pop()
                result.append(cwd)
                for dir in sorted(cwd.dirs.values(), key=lambda d: d.path, reverse=True):
                    dirs.append(dir)
        return result

    def set_state_from_terminal_log(self, terminal_log):
        cmd = ""
        arg = ""
        cwd = self.filesystems["root"].root

        for row in terminal_log.split("\n"):
            m = re.match(r"^[$] ([^ ]+)(?:\s+(.*))?$", row)
            if m:
                cmd = m.group(1)
                arg = str(m.group(2) or "").strip()
                if cmd == "cd":
                    if arg.startswith("/"):
                        cwd = self.get_dir(arg)
                    else:
                        cwd = self.get_dir(cwd.path + "/" + arg)
            else:
                if cmd == "ls":
                    m = re.match(r"^dir (.+)$", row)
                    if m:
                        try:
                            self.get_dir(cwd.path + "/" + m.group(1))
                        except KeyError:
                            cwd.mkdir(m.group(1))
                        continue

                    m = re.match(r"^([0-9]+) (.+)$", row)
                    if m:
                        cwd.add_file(name=m.group(2), size=int(m.group(1)))
                        continue

    def print_info(self, clean=False):
        print("")
        print(f"⋗ {self}")
        for fs in sorted(self.filesystems.values()):
            print(f"  ➔ {fs}")
            dirs = [fs.root]
            while dirs:
                cwd = dirs.pop()
                cwd_path = (cwd.path.lstrip(fs.path).rstrip("/") + "/").lstrip("/")
                cwd_level = len(cwd_path.split("/")) - 1
                print("  " * cwd_level + "  ∴ " + (f"{cwd.name}/" if clean else f"{cwd}"))
                for file in sorted(cwd.files.values(), key=lambda d: d.path):
                    print("  " * (cwd_level + 1) + f"  · " + (f"{file.name}" if clean else f"{file}"))
                for dir in sorted(cwd.dirs.values(), key=lambda d: d.path, reverse=True):
                    dirs.append(dir)
        print("")

    def __str__(self):
        return f"cpu('{self.name}')"
