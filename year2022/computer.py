import re
import sys
from functools import reduce


class File:
    def __init__(self, parent, name, size):
        self.parent = parent
        self.name = name
        self.size = size

    @property
    def path(self):
        return "/" + f"{self.parent.path}/{self.name}".strip("/")

    @property
    def filesystem(self):
        return self.parent if isinstance(self.parent, Filesystem) else self.parent.filesystem

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

    def assign_dir(self, name, dir):
        if name not in self.dirs:
            self.dirs[name] = dir

    def add_file(self, name, size):
        if name not in self.files:
            self.files[name] = File(self, name, size)

    @property
    def size(self):
        return sum([dir.size for dir in self.dirs.values() if dir.filesystem == self.filesystem]) + sum(
            [file.size for file in self.files.values() if file.filesystem == self.filesystem]
        )

    @property
    def path(self):
        return "/" + f"{self.parent.path}/{self.name}".strip("/")

    @property
    def filesystem(self):
        return self.parent if isinstance(self.parent, Filesystem) else self.parent.filesystem

    def __str__(self):
        return f"dir('{self.path}', size={self.size})"


class Filesystem:
    def __init__(self, label, mount, total_space=0):
        if not label:
            raise ValueError("Filesystem label must be set")
        if not mount or mount[0] != "/":
            raise ValueError("Filesystem mount point invalid")

        self.label = label
        self.mount = mount
        self.root = Directory(self, "")
        self.total_space = total_space

    @property
    def available_space(self):
        if not self.total_space:
            return 0
        return self.total_space - self.used_space

    @property
    def used_space(self):
        return self.root.size

    @property
    def path(self):
        return self.mount

    def __str__(self):
        return f"fs('{self.mount}', used={self.used_space}, avail={self.available_space}, label='{self.label}')"


class Command:
    def __init__(self, cmd=None, args=(), cmdline=None, output=None):
        self.echo = False
        self.cmd = (cmd or "").strip()
        self.args = args
        self.output = output
        if cmdline is not None and cmdline.encode() == b"":
            self.cmd = "logout"
            self.echo = True
        if cmdline is not None:
            m = re.match(r"([^ ]+)(?:\s+(.*))?$", cmdline)
            if m:
                self.args = [arg for arg in str(m.group(2) or "").strip().split(" ") if arg]
                self.cmd = m.group(1).strip()
                self.output = None

    def execute(self, interface):
        if self.cmd:
            try:
                func = getattr(self, f"cmd_{self.cmd}")
            except AttributeError:
                interface.out([f"-sh: {self.cmd}: command not found"])
                return

            if self.echo:
                interface.out([self.cmd])

            output = func(interface, self.args, self.output)
            interface.out(output)
            return output

    def cmd_exit(self, interface, args, output=None):
        interface.tty = False

    def cmd_logout(self, interface, args, output=None):
        interface.tty = False

    def cmd_info(self, interface, args, output=None):
        return interface.computer.get_info()

    def cmd_cd(self, interface, args, output=None):
        cpu = interface.computer
        arg = args[0]
        interface.cwd = cpu.get_dir(arg) if arg.startswith("/") else cpu.get_dir(f"{interface.cwd.path}/{arg}")

    def cmd_ls(self, interface, args, output=None):
        cpu = interface.computer

        if output is not None:
            for row in output:
                m = re.match(r"^([^ ]+) (.+)$", row)
                if m and m.group(1) == "dir":
                    try:
                        interface.cwd.assign_dir(m.group(2), cpu.get_dir(f"{interface.cwd.path}/{m.group(2)}"))
                    except KeyError:
                        interface.cwd.mkdir(m.group(2))
                elif m:
                    interface.cwd.add_file(name=m.group(2), size=int(m.group(1)))
            return

        result = []
        objects = sorted(list(interface.cwd.dirs.values()) + list(interface.cwd.files.values()), key=lambda x: x.name)
        for obj in objects:
            if isinstance(obj, Directory):
                result.append(f"dir {obj.name}")
            elif isinstance(obj, File):
                result.append(f"{obj.size} {obj.name}")
        return result

    @property
    def arg(self):
        return " ".join(self.args).strip()


class Interface:
    def __init__(self, computer, tty=True):
        self.computer = computer
        self.tty = tty
        self.cwd = sorted(computer.filesystems.values(), key=lambda x: x.mount)[0].root
        self.output = []

    def connect(self, interactive=True):
        self.tty = True
        while self.tty and interactive:
            sys.stdout.write("$ ")
            sys.stdout.flush()
            cmdline = sys.stdin.readline()
            self.execute(Command(cmdline=cmdline))

    def execute(self, command):
        return command.execute(self)

    def out(self, output):
        self.output = output
        if self.tty and output:
            print("\n".join(output))


class Computer:
    def __init__(self, name, filesystems):
        if not any([fs.mount == "/" for fs in filesystems]):
            raise ValueError("No root filesystem")
        if len(set([fs.mount for fs in filesystems])) != len(filesystems):
            raise ValueError("Multiple filesystems with the same mount point")
        if len(set([fs.label for fs in filesystems])) != len(filesystems):
            raise ValueError("Multiple filesystems with the same label")

        self.name = name
        self.filesystems = {fs.label: fs for fs in filesystems}

    def _get_path(self, path):
        return "/" + "/".join(
            reduce(lambda a, b: ((a + [b]) if b != ".." else a[:-1]) if b else a, [p for p in path.split("/") if p], [])
        )

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
        fs_path = path[len(filesystem.mount) :]
        dir = filesystem.root
        for p in fs_path.split("/"):
            if p:
                dir = dir.dirs[p]
        return dir

    def get_all_dirs(self):
        result = []
        fs = sorted(self.filesystems.values(), key=lambda x: x.mount)[0]
        dirs = [fs.root]
        while dirs:
            cwd = dirs.pop()
            result.append(cwd)
            for dir in sorted(cwd.dirs.values(), key=lambda d: d.path, reverse=True):
                dirs.append(dir)
        return result

    def get_all_files(self):
        result = []
        fs = sorted(self.filesystems.values(), key=lambda x: x.mount)[0]
        dirs = [fs.root]
        while dirs:
            cwd = dirs.pop()
            for file in sorted(cwd.files.values(), key=lambda f: f.name):
                result.append(file)
            for dir in sorted(cwd.dirs.values(), key=lambda d: d.path, reverse=True):
                dirs.append(dir)
        return result

    def get_info(self, clean=False):
        result = []
        result.append(f"⋗ {self}")
        fs = sorted(self.filesystems.values(), key=lambda x: x.mount)[0]
        dirs = [fs.root]
        while dirs:
            cwd = dirs.pop()
            cwd_path = (cwd.path.lstrip(fs.path).rstrip("/") + "/").lstrip("/")
            cwd_level = len(cwd_path.split("/")) - 1
            if isinstance(cwd.parent, Filesystem):
                result.append("  " * cwd_level + "➔ " + (f"{cwd.name}/" if clean else f"{cwd.parent}"))
            else:
                result.append("  " * cwd_level + "∴ " + (f"{cwd.name}/" if clean else f"{cwd}"))
            for file in sorted(cwd.files.values(), key=lambda d: d.path):
                result.append("  " * (cwd_level + 1) + "· " + (file.name if clean else f"{file}"))
            for dir in sorted(cwd.dirs.values(), key=lambda d: d.path, reverse=True):
                dirs.append(dir)
        result.append("")
        return result

    def get_commands_from_terminal_log(self, terminal_log):
        groups = []
        for row in terminal_log.split("\n"):
            if row.startswith("$ "):
                groups.append([])
            groups[-1].append(row)

        commands = []
        for group in groups:
            m = re.match(r"^[$] ([^ ]+)(?:\s+(.*))?$", group[0])
            if m:
                args = [arg for arg in str(m.group(2) or "").strip().split(" ") if arg]
                commands.append(Command(cmd=m.group(1), args=args, output=group[1:]))

        return commands

    def set_state_from_terminal_log(self, terminal_log):
        commands = self.get_commands_from_terminal_log(terminal_log)
        interface = Interface(self, False)

        for command in commands:
            interface.execute(command)

    def __str__(self):
        return f"computer('{self.name}')"
