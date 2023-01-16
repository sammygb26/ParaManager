import sys
from datetime import datetime
from typing import Any

from .ProtoParameter import ProtoParameter
from .Parameter import Parameter

VERSION_PREFIX = "v-"
NAME_PREFIX = "# "


def get_versions_of_file(lines: list[str]):
    versions = []
    for i, line in enumerate(lines):
        if line.startswith(VERSION_PREFIX):
            versions.append((parse_version_line(line), i))
    return versions


def parse_version_line(line: str):
    line = line.removeprefix(VERSION_PREFIX)
    while line.endswith("\n"):
        line = line.removesuffix("\n")

    return int(line)


def get_last_index_of_version(lines: list[str], version: int):
    versions = get_versions_of_file(lines)

    if not versions:
        return 0

    for v, i in reversed(versions):
        if v == version:
            return i


def get_last_version_of_file(lines: list[str]):
    versions = get_versions_of_file(lines)
    if not versions:
        return 0

    v, _ = versions[len(versions) - 1]
    return v


def is_end_line(line: str):
    return "!" in line


def read_file_lines(filename: str):
    try:
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        return lines
    except FileNotFoundError:
        return []


class ParameterSet:
    def __init__(self, proto_parameters: list[ProtoParameter], name: str = None, read_version: int = None):
        self.proto_parameters: list[ProtoParameter] = proto_parameters
        self.name: str = name
        self.read_version: ProtoParameter = ProtoParameter("read_version", read_version, int)
        self.parameters: dict[str, Parameter] = {}

        self.update_parameters()

    def __str__(self) -> str:
        return f"{[str(p) for p in self.parameters.values()]}"

    def __getitem__(self, parameter_name: str) -> Any:
        if parameter_name in self.parameters:
            return self.parameters[parameter_name].value

    def __setitem__(self, name: str, value: Any):
        for p in self.proto_parameters:
            if name not in p.pseudonyms:
                continue
            p.set_value(value)
            self.parameters[p.name] = p()

    def get_all(self, *parameter_names: str) -> list[Any]:
        return [self[name] for name in parameter_names]

    def pretty_print(self) -> None:
        print()
        if self.name:
            print(f"[{self.name}]")
        for p in self.proto_parameters:
            if p.required and not p.set:
                print(f"{p.name} -> NOT SET")
            else:
                print(f"{p.name} -> {str(p.value)}")

    def update_parameters(self) -> None:
        for p in self.proto_parameters:
            self.parameters[p.name] = p()

    def get_unset_required_proto_parameters(self) -> list[ProtoParameter]:
        return [p for p in self.proto_parameters if p.required and not p.set]

    def check_unset_parameters(self) -> None:
        unset_required = self.get_unset_required_proto_parameters()
        if unset_required:
            for p in unset_required:
                print(f"{p.name} not set, can use pseudonyms {p.pseudonyms}")
            raise ValueError(f"Required parameters '{[p.name for p in unset_required]}' not set.")

    def write_file(self, filename: str):
        version = get_last_version_of_file(read_file_lines(filename)) + 1

        file = open(filename, 'a')
        if self.name:
            file.write(f"\n{NAME_PREFIX}{self.name}\n")
        file.write(f'{VERSION_PREFIX}{version}\n')
        file.write(f"t-{datetime.now().strftime('%d/%m/%Y %H-%M-%S')}\n\n")

        file.writelines([f"{p}\n" for p in self.parameters.values()])
        file.write("!\n")
        file.close()

    def read_argv(self, args=None, check_unset_parameters: bool = True):
        if args is None:
            args = sys.argv[1:]
        for name, val in [(args[i], args[i+1]) for i in range(0, len(args), 2)]:
            if name == "-read":
                self.read_file(val, False)
            if name == "-version":
                self.read_version.set_value(val)

            if not name.startswith("-"):
                continue
            self.__setitem__(name.removeprefix("-"), val)

        if check_unset_parameters:
            self.check_unset_parameters()


    def read_line(self, line: str):
        line.replace(" ", "")

        if ":" not in line:
            return
        if len(line.split(":")) != 2:
            return

        self.__setitem__(*line.split(":"))

    def read_file(self, filename: str, check_unset_parameters: bool = True):
        lines = read_file_lines(filename)
        if not lines:
            print(f"Attempt to read empty/nonexistent file '{filename}'")
            return

        read_version = self.read_version().value
        start = get_last_index_of_version(lines, read_version) if read_version else 0
        for line in lines[start:]:
            if is_end_line(line):
                return
            self.read_line(line)

        if check_unset_parameters:
            self.check_unset_parameters()
