import io
import itertools
import pathlib

import pytest

example_input_string = """\
30373
25512
65332
33549
35390
"""

example_first_star_output = 21
example_second_star_output = 8


class TreeGrid(tuple):
    def __new__(cls, input_file):
        return super().__new__(
            cls, (tuple(map(int, line)) for line in stripped_input_lines(input_file))
        )

    def get_column(self, n):
        return tuple(self[i][n] for i in range(len(self)))


def test_tree_grid(example_input):
    grid = TreeGrid(example_input)
    assert grid[0] == (3, 0, 3, 7, 3)
    assert grid.get_column(0) == (3, 2, 6, 3, 3)


def first_star(input_file):
    grid = TreeGrid(input_file)
    sum_visible = 0
    for row_num, row in enumerate(grid):
        for col_num, entry in enumerate(row):
            west_trees = row[:col_num]
            if not west_trees or max(west_trees) < entry:
                sum_visible += 1
                continue
            east_trees = row[col_num + 1 :]
            if not east_trees or max(east_trees) < entry:
                sum_visible += 1
                continue
            column = grid.get_column(col_num)
            north_trees = column[:row_num]
            if not north_trees or max(north_trees) < entry:
                sum_visible += 1
                continue
            south_trees = column[row_num + 1 :]
            if not south_trees or max(south_trees) < entry:
                sum_visible += 1
                continue
    return sum_visible


def second_star(input_file):
    grid = TreeGrid(input_file)
    best_scenic_score = 0
    for row_num, row in enumerate(grid):
        for col_num, entry in enumerate(row):
            trees_looking_west = reversed(row[:col_num])
            west_viewing_distance = 0
            for tree in trees_looking_west:
                west_viewing_distance += 1
                if entry <= tree:
                    break

            trees_looking_east = row[col_num + 1 :]
            east_viewing_distance = 0
            for tree in trees_looking_east:
                east_viewing_distance += 1
                if entry <= tree:
                    break

            column = grid.get_column(col_num)

            trees_looking_north = reversed(column[:row_num])
            north_viewing_distance = 0
            for tree in trees_looking_north:
                north_viewing_distance += 1
                if entry <= tree:
                    break

            trees_looking_south = column[row_num + 1 :]
            south_viewing_distance = 0
            for tree in trees_looking_south:
                south_viewing_distance += 1
                if entry <= tree:
                    break

            scenic_score = (
                west_viewing_distance
                * east_viewing_distance
                * north_viewing_distance
                * south_viewing_distance
            )
            best_scenic_score = max(scenic_score, best_scenic_score)

    return best_scenic_score


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
