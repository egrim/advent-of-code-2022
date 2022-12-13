import io
import itertools
import pathlib
from ast import literal_eval
from typing import Iterable

import pytest

UNDEFINED = object()

example_input_string = """\
[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]
"""

example_first_star_output = 13
example_second_star_output = 140


def pairs(input_file):
    line_generator = stripped_input_lines(input_file)
    while True:
        left_str = next(line_generator)
        right_str = next(line_generator)
        yield literal_eval(left_str), literal_eval(right_str)

        if next(line_generator, None) is None:
            break


class ListComparableWithInt(list):
    def __init__(self, iterable):
        super().__init__()
        for item in iterable:
            if isinstance(item, list):
                self.append(ListComparableWithInt(item))
            else:
                self.append(item)

    def __lt__(self, other):
        if isinstance(other, int):
            other = [other]
        return super().__lt__(other)

    def __gt__(self, other):
        if isinstance(other, int):
            other = [other]
        return super().__gt__(other)


def first_star(input_file):
    correct_indices = []
    for index, (left, right) in enumerate(pairs(input_file), start=1):
        left = ListComparableWithInt(left)
        right = ListComparableWithInt(right)
        if left < right:
            correct_indices.append(index)

    return sum(correct_indices)


def second_star(input_file):
    divider_packets = ListComparableWithInt(([[2]], [[6]]))
    line_generator = stripped_input_lines(input_file)
    packets = list(divider_packets)
    while (line := next(line_generator, None)) is not None:
        if line:
            packet = ListComparableWithInt(literal_eval(line))
            packets.append(packet)
    packets.sort()
    first_index = packets.index(divider_packets[0]) + 1
    second_index = packets.index(divider_packets[1]) + 1
    return first_index * second_index


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
