from __future__ import annotations

import io
import pathlib
from dataclasses import dataclass, field
from functools import cached_property

import pytest

example_input_string = """\
$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
"""

example_first_star_output = 95437
example_second_star_output = 24933642


@dataclass
class File:
    size: int


@dataclass
class Directory:
    entries: dict[str : File | Directory] = field(default_factory=dict)

    @cached_property
    def size(self):
        return sum(entry.size for entry in self.entries.values())

    @property
    def subdirectories(self):
        return tuple(
            entry for entry in self.entries.values() if isinstance(entry, Directory)
        )

    def recursively_traverse(self):
        for directory in self.subdirectories:
            yield from directory.recursively_traverse()

        yield self


def first_star(input_file):
    root = get_root(input_file)
    return sum(
        directory.size
        for directory in root.recursively_traverse()
        if directory.size <= 100000
    )


def get_root(input_file):
    root = Directory()
    directory_stack = [root]
    for line in stripped_input_lines(input_file):
        cwd = directory_stack[-1]
        match line.split(" "):
            case "$", "ls":
                pass
            case "$", "cd", param:
                match param:
                    case "..":
                        directory_stack.pop()
                    case "/":
                        directory_stack = [root]
                    case new_dir:
                        directory_stack.append(cwd.entries[new_dir])
            case "dir", dir_name:
                cwd.entries[dir_name] = Directory()
            case size, file_name:
                cwd.entries[file_name] = File(size=int(size))
    return root


def second_star(input_file):
    space_total = 70000000
    space_needed = 30000000

    root = get_root(input_file)
    space_free = space_total - root.size

    min_space_to_delete = space_needed - space_free
    return min(
        directory.size
        for directory in root.recursively_traverse()
        if directory.size > min_space_to_delete
    )


# noinspection DuplicatedCode
def main():
    input_path = pathlib.Path("input", pathlib.Path(__file__).name).with_suffix(".txt")

    print(f"First star answer: {first_star(input_path.open())}")
    print(f"Second star answer: {second_star(input_path.open())}")


@pytest.fixture
def example_input():
    return io.StringIO(example_input_string)


def test_first_star(example_input):
    assert first_star(example_input) == example_first_star_output


def test_second_star(example_input):
    assert second_star(example_input) == example_second_star_output


def test_main():
    main()


def stripped_input_lines(input_file):
    return (line.strip() for line in input_file)


if __name__ == "__main__":
    main()
