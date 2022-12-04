import io
import pathlib

import pytest

example_input_string = """\
2-4,6-8
2-3,4-5
5-7,7-9
2-8,3-7
6-6,4-6
2-6,4-8
"""

example_first_star_output = 2
example_second_star_output = 4


def first_star(input_file):
    count = 0
    for line in stripped_input_lines(input_file):
        first_elf, second_elf = line.split(',')
        first_elf_start, first_elf_stop = map(int, first_elf.split('-'))
        second_elf_start, second_elf_stop = map(int, second_elf.split('-'))
        if ((first_elf_start <= second_elf_start and second_elf_stop <= first_elf_stop) or
            (second_elf_start <= first_elf_start and first_elf_stop <= second_elf_stop)):
            count += 1

    return count


def second_star(input_file):
    count = 0
    for line in stripped_input_lines(input_file):
        first_elf, second_elf = line.split(',')
        first_elf_start, first_elf_stop = map(int, first_elf.split('-'))
        second_elf_start, second_elf_stop = map(int, second_elf.split('-'))
        if ((first_elf_start <= second_elf_start and second_elf_start <= first_elf_stop) or
            (second_elf_start <= first_elf_start and first_elf_start <= second_elf_stop)):
            count += 1

    return count


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


if __name__ == '__main__':
    main()
