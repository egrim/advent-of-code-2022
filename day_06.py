import io
import itertools
import pathlib

import pytest

examples = [
    ("mjqjpqmgbljsphdztnvjfqwrcgsmlb", 7),
    ("bvwbjplbgvbhsrlpgdmjqwftvncz", 5),
    ("nppdvjthqldpwncqszvftbrmjlhg", 6),
    ("nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg", 10),
    ("zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw", 11)
]


def find_marker(input, consecutive_distincts):
    input = input.read()
    i = 0
    while len(n := input[i:i+consecutive_distincts]) == consecutive_distincts:
        if len(set(n)) == consecutive_distincts:
            return i + consecutive_distincts
        i += 1
    else:
        raise ValueError

def first_star(input):
    return find_marker(input, 4)


def second_star(input):
    return find_marker(input, 14)


# noinspection DuplicatedCode
def main():
    input_path = pathlib.Path("input", pathlib.Path(__file__).name).with_suffix(".txt")

    print(f"First star answer: {first_star(input_path.open())}")
    print(f"Second star answer: {second_star(input_path.open())}")


@pytest.mark.parametrize("test_input, expected", examples)
def test_first_star(test_input, expected):
    assert first_star(io.StringIO(test_input)) == expected


@pytest.mark.parametrize("test_input, expected", examples)
def test_second_star(test_input, expected):
    assert second_star(io.StringIO(test_input)) == expected


def test_main():
    main()


def stripped_input_lines(input_file):
    return (line.strip() for line in input_file)


if __name__ == '__main__':
    main()
