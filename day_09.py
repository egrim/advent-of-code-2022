import io
import pathlib
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import pairwise

import pytest

example_first_star_input_string = """\
R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
"""

example_first_star_output = 13

example_second_star_input_string = """\
R 5
U 8
L 8
D 3
R 17
D 10
L 25
U 20
"""

example_second_star_output = 36


@dataclass
class Position:
    x: int = 0
    y: int = 0
    tail_visited: bool = False


class Grid:
    contents: dict[int : dict[int:Position]]
    rope: list[Position]
    start: Position

    def __init__(self, rope_length=2):
        self.start = Position(tail_visited=True)
        self.rope = [self.start] * rope_length
        self.contents = defaultdict(dict)
        self.contents[0][0] = self.start

    def get_and_create_if_needed(self, x, y):
        try:
            return self.contents[y][x]
        except KeyError:
            new_position = Position(x, y)
            self.contents[y][x] = new_position
            return new_position

    def move_head_up(self):
        new_x, new_y = self.rope[0].x, (self.rope[0].y - 1)
        self.move_head_to(new_x, new_y)

    def move_head_down(self):
        new_x, new_y = self.rope[0].x, (self.rope[0].y + 1)
        self.move_head_to(new_x, new_y)

    def move_head_left(self):
        new_x, new_y = (self.rope[0].x - 1), self.rope[0].y
        self.move_head_to(new_x, new_y)

    def move_head_right(self):
        new_x, new_y = (self.rope[0].x + 1), self.rope[0].y
        self.move_head_to(new_x, new_y)

    def move_head_to(self, x, y):
        new_rope = [self.get_and_create_if_needed(x, y)]
        for knot_to_move in self.rope[1:]:
            x, y = knot_to_move.x, knot_to_move.y
            dx, dy = (new_rope[-1].x - x), (new_rope[-1].y - y)

            if abs(dx) == 2:  # left/right move needed
                x += 1 if dx > 0 else -1
                if abs(dy) == 1:  # diagonal also needed
                    y += 1 if dy > 0 else -1

            if abs(dy) == 2:  # up/down move needed
                y += 1 if dy > 0 else -1
                if abs(dx) == 1:  # diagonal also needed
                    x += 1 if dx > 0 else -1

            new_rope.append(self.get_and_create_if_needed(x, y))

        new_rope[-1].tail_visited = True
        self.rope = new_rope
        # self.visualize()

    def __iter__(self):
        for row in self.contents.values():
            for position in row.values():
                yield position

    def visualize(self):
        row_min = row_max = 0
        col_min = col_max = 0
        for row_num in self.contents:
            row_min = min(row_min, row_num)
            row_max = max(row_max, row_num)
            for col_num in self.contents[row_num]:
                col_min = min(col_min, col_num)
                col_max = max(col_max, col_num)

        print("*" * 80)
        for row_num in range(row_min, row_max + 1):
            row = self.contents.get(row_num, {})
            for col_num in range(col_min, col_max + 1):
                position = row.get(col_num, None)

                if position is None:
                    print_char = " "
                else:
                    try:
                        index = self.rope.index(position)
                        if index == 0:
                            print_char = "H"
                        elif index == len(self.rope) - 1:
                            print_char = "T"
                        else:
                            print_char = str(index)
                    except ValueError:
                        if position == self.start:
                            print_char = "s"
                        elif position.tail_visited:
                            print_char = "#"
                        else:
                            print_char = "."
                print(print_char, end="")
            print()
        print("*" * 80)


def get_count_of_visited(input_file, rope_length):
    grid = Grid(rope_length)
    for line in stripped_input_lines(input_file):
        direction, count = line.split()
        count = int(count)
        match direction:
            case "L":
                move_func = grid.move_head_left
            case "R":
                move_func = grid.move_head_right
            case "U":
                move_func = grid.move_head_up
            case "D":
                move_func = grid.move_head_down
            case _:
                raise ValueError
        for _ in range(count):
            move_func()

    return len(list(position for position in grid if position.tail_visited))


def first_star(input_file):
    return get_count_of_visited(input_file, 2)


def second_star(input_file):
    return get_count_of_visited(input_file, 10)


# noinspection DuplicatedCode
def main():
    input_path = pathlib.Path("input", pathlib.Path(__file__).name).with_suffix(".txt")

    print(f"First star answer: {first_star(input_path.open())}")
    print(f"Second star answer: {second_star(input_path.open())}")


def test_first_star():
    example_input = io.StringIO(example_first_star_input_string)
    assert first_star(example_input) == example_first_star_output


def test_second_star():
    example_input = io.StringIO(example_second_star_input_string)
    assert second_star(example_input) == example_second_star_output


def test_main():
    main()


def stripped_input_lines(input_file):
    return (line.strip() for line in input_file)


if __name__ == "__main__":
    main()
