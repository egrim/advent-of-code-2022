from __future__ import annotations

import io
import pathlib
import sys
from dataclasses import dataclass

import pytest

UNDEFINED = object()

example_input_string = """\
Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
"""

example_first_star_output = 31
example_second_star_output = 29


@dataclass
class Node:
    pos_x: int = None
    pos_y: int = None
    height: chr = None

    visited: bool = False
    short_path_distance: int = sys.maxsize
    short_path_previous_node = None


NO_DEFAULT = object()


class Grid:
    def __init__(self, input_file):
        self.nodes = {}
        self.a_nodes = []
        for row_num, line in enumerate(stripped_input_lines(input_file)):
            row_dict = {}
            for char_num, char in enumerate(line):
                node = Node(pos_x=char_num, pos_y=row_num)
                row_dict[char_num] = node
                if char == "S":
                    node.height = "a"
                    self.marked_start = node
                elif char == "E":
                    node.height = "z"
                    self.marked_end = node
                else:
                    node.height = char

                if char == "a":
                    self.a_nodes.append(node)

            self.nodes[row_num] = row_dict

    def get_node_at(self, pos_x, pos_y, default=NO_DEFAULT):
        try:
            return self.nodes[pos_y][pos_x]
        except KeyError:
            if default is not NO_DEFAULT:
                return default
            else:
                raise

    def get_neighbors(self, node, max_height=1):
        x, y = node.pos_x, node.pos_y
        neighbor_slots = [
            self.get_node_at(nx, ny, None)
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
        ]
        neighbors_short_enough = [
            neighbor
            for neighbor in neighbor_slots
            if neighbor is not None
            and ord(neighbor.height) - ord(node.height) <= max_height
        ]
        return neighbors_short_enough

    def do_the_dijkstra(self, starting_points=None):
        if starting_points is None:
            starting_points = (self.marked_start,)

        for starting_point in starting_points:
            starting_point.short_path_distance = 0

        unvisited = list(starting_points)
        assert len(unvisited) != 0

        while unvisited:
            unvisited.sort(key=lambda node: node.short_path_distance)
            current = unvisited.pop(0)

            if current == self.marked_end:
                break

            distance_to_neighbors = current.short_path_distance + 1
            for neighbor in self.get_neighbors(current):
                if not neighbor.visited:
                    if distance_to_neighbors < neighbor.short_path_distance:
                        neighbor.short_path_distance = distance_to_neighbors
                        neighbor.short_path_previous_node = current
                        if neighbor not in unvisited:
                            unvisited.append(neighbor)

            current.visited = True

        if current != self.marked_end:
            return None
        else:
            return current.short_path_distance


def first_star(input_file):
    grid = Grid(input_file)
    return grid.do_the_dijkstra()


def second_star(input_file):
    grid = Grid(input_file)
    return grid.do_the_dijkstra(grid.a_nodes)


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
