import io
import itertools
import pathlib
import sys
from ast import literal_eval
from collections import defaultdict

import pytest
from attr import dataclass

UNDEFINED = object()

example_input_string = """\
498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9
"""

example_first_star_output = 24
example_second_star_output = 93


@dataclass
class Position:
    x: int
    y: int
    has_rock: bool = False
    has_sand: bool = False

    def is_empty(self):
        return self.has_rock == False and self.has_sand == False


def inclusive_interval_range(first, second):
    if first < second:
        return range(first, second + 1)
    else:
        return range(second, first + 1)


class Space:
    def __init__(self, input_file, add_floor=False):
        self.min_x = sys.maxsize
        self.min_y = sys.maxsize
        self.max_x = -sys.maxsize
        self.max_y = -sys.maxsize

        self.add_floor = False  # Disable while populating

        self.positions = {}
        for path in stripped_input_lines(input_file):
            for begin, end in itertools.pairwise(path.split(" -> ")):
                x_begin, y_begin = literal_eval(begin)
                x_end, y_end = literal_eval(end)

                for y in inclusive_interval_range(y_begin, y_end):
                    for x in inclusive_interval_range(x_begin, x_end):
                        position = self.get(x, y, create=True)
                        position.has_rock = True

        self.floor_y = self.max_y + 2
        if add_floor:
            for x in inclusive_interval_range(self.min_x, self.max_x):
                position = self.get(x, self.floor_y, create=True)
                position.has_rock = True
        self.add_floor = True

        self.start = self.get(500, 0, create=True)

    def get(self, x, y, create=False):
        try:
            return self.positions[x][y]
        except KeyError:
            if not create:
                raise ValueError

            col = self.positions.get(x)
            if col is None:
                self.positions[x] = col = {}
                if self.add_floor:
                    col[self.floor_y] = Position(x, self.floor_y, has_rock=True)

            position = col.get(y)
            if position is None:
                position = col[y] = Position(x, y)

            self.update_bounds(x, y)
            return position

    def generate_sand_and_get_resting_position(self):
        position = self.start
        while next := self.get_next_position(position):
            if next is position:
                position.has_sand = True
                return position
            else:
                position = next

    def get_next_position(self, position):
        # Check for void
        column = self.positions[position.x]
        if all(
            below_position.is_empty()
            for y, below_position in column.items()
            if y > position.y
        ):
            return None

        x, y = position.x, position.y
        candidate_positions = (
            (x, y + 1),  # down
            (x - 1, y + 1),  # down+left
            (x + 1, y + 1),  # down+right
        )

        for new_x, new_y in candidate_positions:
            new_position = self.get(new_x, new_y, create=True)
            if new_position.is_empty():
                return new_position

        return position  # stuck

    def update_bounds(self, x, y):
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.min_y = min(self.min_y, y)
        self.max_y = max(self.max_y, y)

    def visualize(self):
        visualization = []
        for y in range(self.min_y, self.max_y + 1):
            for x in range(self.min_x, self.max_x + 1):
                try:
                    position = self.get(x, y)
                    if position.has_sand:
                        visualization.append("O")
                    elif position == self.start:
                        visualization.append("+")
                    elif position.has_rock:
                        visualization.append("#")
                    else:
                        visualization.append(".")
                except ValueError:
                    visualization.append(".")
            visualization.append("\n")
        return "".join(visualization)


def first_star(input_file):
    space = Space(input_file)
    count = 0
    while space.generate_sand_and_get_resting_position():
        count += 1
    return count


def second_star(input_file):
    space = Space(input_file, add_floor=True)
    count = 0
    while position := space.generate_sand_and_get_resting_position():
        count += 1
        if position == space.start:
            break
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


if __name__ == "__main__":
    main()
