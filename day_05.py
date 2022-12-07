import collections
import io
import itertools
import pathlib
import re

import pytest

example_input_string = """\
    [D]    
[N] [C]    
[Z] [M] [P]
 1   2   3 

move 1 from 2 to 1
move 3 from 1 to 3
move 2 from 2 to 1
move 1 from 1 to 2
"""

example_first_star_output = "CMZ"
example_second_star_output = "MCD"


CRATE_NUMBERS = re.compile(r"^(?: (?P<crate_num>\d+)  ?)+")
CRATE_MOVES = re.compile(r"move (?P<moves>\d+) from (?P<from>\d+) to (?P<to>\d+)")


def chunk(string, n):
    it = iter(string)
    while chunk := "".join(itertools.islice(it, n)):
        yield chunk


def parse_starting_positions(input_file):
    crates = collections.defaultdict(list)
    for line in input_file:
        line = line.rstrip("\n")
        if crate_number_match := CRATE_NUMBERS.match(line):
            break
        for num, crate in enumerate(chunk(line, 4), 1):
            crate = crate.strip()
            if crate:
                crates[num].append(crate[1:-1])
    else:
        raise ValueError  # reached end of file before finding crate number row
    assert int(crate_number_match["crate_num"]) == len(crates)
    return crates


def first_star(input_file):
    crates = parse_starting_positions(input_file)

    for line in input_file:
        line = line.rstrip("\n")
        if crate_move_match := CRATE_MOVES.match(line):
            moves, frm, to = map(int, crate_move_match.groups())
            for _ in range(moves):
                crates[to].insert(0, crates[frm].pop(0))

    return "".join(crates[i + 1][0] for i in range(len(crates)))


def second_star(input_file):
    crates = parse_starting_positions(input_file)

    for line in input_file:
        line = line.rstrip("\n")
        if crate_move_match := CRATE_MOVES.match(line):
            moves, frm, to = map(int, crate_move_match.groups())
            crates[to][0:0] = crates[frm][0:moves]
            crates[frm] = crates[frm][moves:]

    return "".join(crates[i + 1][0] for i in range(len(crates)))


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
