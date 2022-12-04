import io
import itertools
import pathlib

import pytest

example_input_string = """\
vJrwpWtwJgWrhcsFMMfFFhFp
jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
PmmdzqPrVvPwwTWBwg
wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
ttgJtRGJQctTZtZT
CrZsJsPPZsGzwwsLwLmpwMDw
"""

example_first_star_output = 157
example_second_star_output = 70


def get_priority(char):
    if 'a' <= char <= 'z':
        return 1 + ord(char) - ord('a')
    elif 'A' <= char <= 'Z':
        return 27 + ord(char) - ord('A')
    else:
        raise ValueError


def three_lines_at_a_time(input_file):
    line_generator = stripped_input_lines(input_file)
    while lines := tuple(itertools.islice(line_generator, 3)):
        yield lines


def first_star(input_file):
    total = 0
    for line in stripped_input_lines(input_file):
        length = len(line)
        assert length % 2 == 0
        half_length = int(len(line) / 2)
        first, second = line[:half_length], line[half_length:]
        for letter in set(first) & set(second):
            total += get_priority(letter)

    return total


def second_star(input_file):
    total = 0
    for first, second, third in three_lines_at_a_time(input_file):
        for letter in set(first) & set(second) & set(third):
            total += get_priority(letter)

    return total


# noinspection DuplicatedCode
def main():
    input_path = pathlib.Path("input", pathlib.Path(__file__).name).with_suffix(".txt")

    print(f"First star answer: {first_star(input_path.open())}")
    print(f"Second star answer: {second_star(input_path.open())}")


@pytest.fixture
def test_input():
    return io.StringIO(example_input_string)


def test_first_star(test_input):
    assert first_star(test_input) == example_first_star_output


def test_second_star(test_input):
    assert second_star(test_input) == example_second_star_output


def stripped_input_lines(input_file):
    return (line.strip() for line in input_file)


if __name__ == '__main__':
    main()
