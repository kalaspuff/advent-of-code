import asyncio
import datetime
import re
from functools import reduce

from prompt_toolkit import PromptSession
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style

# from prompt_toolkit.history import InMemoryHistory
# from prompt_toolkit.formatted_text import to_formatted_text
# from prompt_toolkit.renderer import print_formatted_text


class File:
    def __init__(self, parent, name, size=0, content=""):
        self.parent = parent
        self.name = name

        if content:
            size = len(content)

        self.size = size
        self.content = content

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

    def add_file(self, name, size=0, content=""):
        if name not in self.files:
            self.files[name] = File(self, name, size=size, content=content)

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
    def free_space(self):
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
        return f"fs('{self.mount}', used={self.used_space}, free={self.free_space}, label='{self.label}')"


class Command:
    def __init__(self, cmdline=None, cmd=None, args=(), output=None):
        self.echo = False
        self.cmd = (cmd or "").strip()
        self.args = args
        self.output = output

        if cmdline is not None:
            if cmdline.encode() == b"":
                self.cmd = "logout"
                self.echo = True

            m = re.match(r"([^ ]+)(?:\s+(.*))?$", cmdline)
            if m:
                self.args = [arg for arg in str(m.group(2) or "").strip().split(" ") if arg]
                self.cmd = m.group(1).strip()

        if self.cmd in ("exit", "quit"):
            self.cmd = "logout"

    def execute(self, interface):
        output = []

        if not self.cmd:
            return output

        if not re.match(r"^[a-z0-9_]+$", self.cmd):
            interface.error_out([f"[err] ⌁ {self.cmd}: command not found"])
            return output

        try:
            func = getattr(self, f"cmd_{self.cmd}")
        except AttributeError:
            interface.error_out([f"[err] ⌁ {self.cmd}: command not found"])
            return output

        if self.echo:
            interface.echo_out([self.cmd])

        try:
            output = func(interface, self.args, self.output)
        except Exception as exc:
            interface.error_out([f"[err] ⌁ {self.cmd}: {exc}"])
            return output

        interface.out(output)
        return output

    def cmd_logout(self, interface, args, output=None):
        interface.disconnect()

    def cmd_info(self, interface, args, output=None):
        return interface.computer.get_info()

    def cmd_pwd(self, interface, args, output=None):
        return [interface.cwd.path]

    def cmd_mkdir(self, interface, args, output=None):
        try:
            parent = interface.get_relative_dir(args[0] + "/..")
        except Exception:
            closest_parent = None
            i = 1
            while not closest_parent:
                i += 1
                try:
                    closest_parent = interface.get_relative_dir(args[0] + "/.." * i)
                except Exception:
                    pass
            missing_dir = interface.get_relative_dir(args[0] + "/.." * (i - 1), return_str_path=True)
            raise Exception(f"{missing_dir}: No such file or directory")

        name = args[0].rstrip("/").split("/")[-1]

        if name in ("", ".", ".."):
            raise Exception(f"{args[0]}: File exists")
        if name in parent.dirs:
            raise Exception(f"{args[0]}: File exists")
        if name in parent.files:
            raise Exception(f"{args[0]}: File exists")

        parent.mkdir(name)

    def cmd_touch(self, interface, args, output=None):
        try:
            parent = interface.get_relative_dir(args[0] + "/..")
        except Exception:
            closest_parent = None
            i = 1
            while not closest_parent:
                i += 1
                try:
                    closest_parent = interface.get_relative_dir(args[0] + "/.." * i)
                except Exception:
                    pass
            missing_dir = interface.get_relative_dir(args[0] + "/.." * (i - 1), return_str_path=True)
            raise Exception(f"{missing_dir}: No such file or directory")

        name = args[0].rstrip("/").split("/")[-1]

        if name in ("", ".", ".."):
            raise Exception(f"{args[0]}: File exists")
        if name in parent.dirs:
            raise Exception(f"{args[0]}: File exists")
        if name in parent.files:
            return

        parent.add_file(name)

    def cmd_cd(self, interface, args, output=None):
        try:
            interface.cwd = interface.homedir if not args else interface.get_relative_dir(args[0])
        except KeyError:
            raise Exception(f"{args[0]}: No such file or directory")

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
                    interface.cwd.add_file(m.group(2), size=int(m.group(1)))
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
    tty = True
    output = []
    error_output = []
    error = False

    def __init__(self, computer, tty=True):
        self.computer = computer
        self.tty = tty
        self.homedir = sorted(computer.filesystems.values(), key=lambda x: x.mount)[0].root
        self.cwd = self.homedir
        self.output = []
        self.error_output = []
        self.error = False
        self.username = "elf"

    async def connect(self, interactive=True):
        self.tty = True

        session = PromptSession()
        bindings = KeyBindings()

        style = Style.from_dict(
            {
                # User input (default text).
                # "": "#aaaa88 bold",
                "": "#bbaabb bold",
                # Prompt.
                "username": "#44ff44 bold",
                "at": "#aaaaaa",
                "device": "#ffff44 bold",
                "square": "#aaaa88 bold",
                "pound": "#884444 bold",
                "time": "#ff0000 bold",
                "day": "#ff00ff bold",
                # "path_delimiter": "#4444aa bold",
                # "path": "#8888ee bold",
                # "path_delimiter": "#338833 bold",
                # "path": "#00aa00 bold",
                "path_delimiter": "#444444 bold",
                "path": "#8888ee bold",
                "active_path": "#8888ee bold",
                # Right prompt.
                "rprompt": "#202020 bg:#efdd74 bold",
                # Bottom toolbar.
                "bottom-toolbar": "#111111 bg:#aaaaaa bold",
                "bottom-toolbar.green": "bg:#5cc040",
                "bottom-toolbar.red": "bg:#f04040",
                "bottom-toolbar.yellow": "bg:#f0f040",
                "bottom-toolbar.symbol": "bg:#606060",
                "bottom-toolbar.triangle": "bg:#8080f0",
                # "bottom-toolbar": "#5cc040 bg:#000000 bold",
                # "bottom-toolbar.box": "bg:#aaaaaa",
                # "bottom-toolbar.delimiter": "bg:#145410",
                # "bottom-toolbar.info": "bg:#000000",
                # "bottom-toolbar.title": "bg:#000000",
                # "bottom-toolbar": "#acc040 bg:#000000 bold",
                # "bottom-toolbar.box": "bg:#aaaaaa",
                # "bottom-toolbar.delimiter": "bg:#444400",
                # "bottom-toolbar.info": "bg:#000000",
                # "bottom-toolbar.title": "bg:#000000",
                # "bottom-toolbar.box": "bg:#aaaaaa",
                # "bottom-toolbar.delimiter": "bg:#aaddaa",
                # "bottom-toolbar.info": "bg:#6677cc",
                # "bottom-toolbar.title": "bg:#6677cc",
                "bottom-toolbar.delimiter2": "bg:#88dddd",
                "bottom-toolbar.info2": "bg:#88bbaa",
                "bottom-toolbar.title2": "bg:#88bbaa",
                "bottom-toolbar.delimiter3": "bg:#aaddaa",
                "bottom-toolbar.info3": "bg:#66cc99",
                "bottom-toolbar.title3": "bg:#66cc99",
            }
        )

        class CustomCompleter(Completer):
            def get_completions(_, document, complete_event):
                if document.text_after_cursor:
                    return

                cmd = ""
                path_search = False
                prefix_completion = ""
                path_arg = ""
                if document.text.lstrip(" ").split(" ", 1)[0] in ("cd", "touch", "mkdir"):
                    cmd = document.text.lstrip(" ").split(" ", 1)[0]
                    path_arg = document.text.lstrip(" ").lstrip(cmd).lstrip(" ")
                    if document.text.lstrip(" ") == cmd:
                        prefix_completion = " "
                    path_search = True

                if path_search:
                    prefix = path_arg
                    last_prefix = prefix
                    cwd = self.cwd
                    path = ""
                    if "/" == prefix:
                        cwd = self.get_relative_dir("/")
                        last_prefix = ""
                        path = "/"
                    elif "/" in prefix:
                        path, last_prefix = prefix.rsplit("/", 1)
                        try:
                            cwd = self.get_relative_dir(path)
                        except Exception:
                            return
                        path += "/"
                    for name in sorted([d.name for d in cwd.dirs.values()]) + (
                        [".."] if (not path or prefix.split("/")[-2:][0] == "..") and cwd.path != "/" else []
                    ):
                        if name.startswith(last_prefix):
                            yield Completion(
                                f"{prefix_completion}{path}{name}/".replace("//", "/"),
                                display=f"➔ {path}{name}",
                                display_meta=self.get_relative_dir(f"{path}{name}").path,
                                start_position=-len(prefix),
                                style="bg:#444444 fg:#ddddcc bold",
                                selected_style="bg:#eeeeff fg:#000000",
                            )

        @bindings.add("c-d")
        def _(event):
            event.app.current_buffer.text = "logout"
            self.disconnect()
            event.app.exit()

        @Condition
        def completion_selected() -> bool:
            app = get_app()
            return (
                app.current_buffer.complete_state is not None and app.current_buffer.complete_state.current_completion
            )

        @bindings.add("tab", filter=completion_selected)
        @bindings.add("right", filter=completion_selected)
        def _(event):
            b = event.current_buffer
            event.app.current_buffer.complete_state = None
            b.insert_text("")

        def bottom_toolbar():
            timedelta = datetime.datetime.now() - datetime.datetime.utcnow()
            timedelta_seconds = round(timedelta.seconds + timedelta.microseconds * 1e-6)
            short_str = (
                datetime.datetime.utcnow()
                .replace(tzinfo=datetime.timezone.utc)
                .astimezone(datetime.timezone(offset=datetime.timedelta(seconds=timedelta_seconds)))
                .strftime("%a %-d %b %Y %H:%M:%S %z")
            )

            event_name = "next AoC"
            event_timedelta = (
                datetime.datetime(
                    datetime.datetime.utcnow().year,
                    datetime.datetime.utcnow().month,
                    datetime.datetime.utcnow().day,
                    5,
                    0,
                    0,
                )
                - datetime.datetime.utcnow()
            )
            if event_timedelta.days < 0:
                event_timedelta = (
                    datetime.datetime(
                        datetime.datetime.utcnow().year,
                        datetime.datetime.utcnow().month,
                        datetime.datetime.utcnow().day,
                        5,
                        0,
                        0,
                    )
                    - datetime.datetime.utcnow()
                    + datetime.timedelta(days=1)
                )

            if event_timedelta.days == 0 and event_timedelta.seconds < 3600:
                event_timedelta_str = f"{((event_timedelta.seconds % 3600) // 60)}m {(event_timedelta.seconds % 60)}s"
            elif event_timedelta.days == 0:
                event_timedelta_str = f"{event_timedelta.seconds // 3600}h {((event_timedelta.seconds % 3600) // 60)}m"
            else:
                event_timedelta_str = f"{event_timedelta.days}d {event_timedelta.seconds // 3600}h {((event_timedelta.seconds % 3600) // 60)}m"

            output = [
                ("class:bottom-toolbar.title2", "❄ "),
                ("class:bottom-toolbar.info", f"{event_timedelta_str} to {event_name}"),
                ("class:bottom-toolbar.title2", " ❄ "),
                ("class:bottom-toolbar.info", short_str),
            ]

            columns = session.app.output.get_size().columns - sum([len(v) for _, v in output])
            msg = "connected ✓"
            msg_style = "class:bottom-toolbar.green"
            # msg = "error ✖"
            # msg_style = "class:bottom-toolbar.red"

            output += [("class:bottom-toolbar", " " * (columns - len(msg))), (msg_style, msg)]

            return output

        async def _invalidate_interval():
            app = session.app
            if not app or app.is_done or not self.tty:
                return
            app.invalidate()
            await asyncio.sleep(0.5)
            asyncio.ensure_future(_invalidate_interval())

        asyncio.ensure_future(_invalidate_interval())
        session.app.refresh_interval = 5

        try:
            while self.tty and interactive:
                message = [
                    ("class:square", "["),
                    ("class:username", self.username),
                    ("class:at", " ➔ "),
                    ("class:device", self.computer.name),
                    ("class:square", "] "),
                ]

                for p in self.cwd.path.split("/")[1:-1]:
                    message.append(("class:path_delimiter", "/"))
                    message.append(("class:path", p))
                message.append(("class:path_delimiter", "/"))
                message.append(("class:active_path", self.cwd.path.split("/")[-1]))

                message.append(("class:pound", " ≡ "))

                with patch_stdout():
                    cmdline = await session.prompt_async(
                        message,
                        bottom_toolbar=bottom_toolbar,
                        key_bindings=bindings,
                        style=style,
                        completer=CustomCompleter(),
                        complete_while_typing=True,
                    )
                if cmdline:
                    self.execute(Command(cmdline))
        except EOFError:
            self.disconnect()

    def disconnect(self):
        self.tty = False

    def get_relative_dir(self, path, return_str_path=False):
        cpu = self.computer
        return (
            cpu.get_dir(path, return_str_path)
            if path.startswith("/")
            else cpu.get_dir(f"{self.cwd.path}/{path}", return_str_path)
        )

    def execute(self, command):
        return command.execute(self)

    def out(self, output):
        self.error = False
        self.output = output or []
        if self.tty and output:
            print("\n".join(output))

    def error_out(self, output):
        self.error = True
        self.error_output = output or []
        if self.tty and output:
            print("\n".join(output))

    def echo_out(self, output):
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
            reduce(
                lambda a, b: ((a + [b]) if b != ".." else a[:-1]) if b else a,
                [p for p in path.split("/") if p and p != "."],
                [],
            )
        )

    def get_filesystem(self, path):
        path = self._get_path(path)

        candidates = []
        for fs in self.filesystems.values():
            if path in (fs.mount, f"{fs.mount}/") or path.startswith(fs.mount.rstrip("/") + "/"):
                candidates.append((len(fs.mount), fs))

        return sorted(candidates, key=lambda x: x[0])[-1][1]

    def get_dir(self, path, return_str_path=False):
        path = self._get_path(path)
        if return_str_path:
            return path
        fs = self.get_filesystem(path)
        relative_path = path[len(fs.mount) :]

        dir = fs.root
        for p in relative_path.split("/"):
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

        return result

    def get_commands_from_terminal_log(self, terminal_log):
        commands = []
        for row in terminal_log.split("\n"):
            if row.startswith("$ "):
                commands.append(Command(row[2:].strip(), output=[]))
            else:
                commands[-1].output.append(row)

        return commands

    def set_state_from_terminal_log(self, terminal_log, interface=None):
        if not interface:
            interface = Interface(self, False)

        commands = self.get_commands_from_terminal_log(terminal_log)

        for command in commands:
            interface.execute(command)

    def __str__(self):
        return f"computer('{self.name}')"
