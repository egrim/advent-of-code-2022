import io
import itertools
import pathlib

import pytest

example_input_string = """\
addx 15
addx -11
addx 6
addx -3
addx 5
addx -1
addx -8
addx 13
addx 4
noop
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx -35
addx 1
addx 24
addx -19
addx 1
addx 16
addx -11
noop
noop
addx 21
addx -15
noop
noop
addx -3
addx 9
addx 1
addx -3
addx 8
addx 1
addx 5
noop
noop
noop
noop
noop
addx -36
noop
addx 1
addx 7
noop
noop
noop
addx 2
addx 6
noop
noop
noop
noop
noop
addx 1
noop
noop
addx 7
addx 1
noop
addx -13
addx 13
addx 7
noop
addx 1
addx -33
noop
noop
noop
addx 2
noop
noop
noop
addx 8
noop
addx -1
addx 2
addx 1
noop
addx 17
addx -9
addx 1
addx 1
addx -3
addx 11
noop
noop
addx 1
noop
addx 1
noop
noop
addx -13
addx -19
addx 1
addx 3
addx 26
addx -30
addx 12
addx -1
addx 3
addx 1
noop
noop
noop
addx -9
addx 18
addx 1
addx 2
noop
noop
addx 9
noop
noop
noop
addx -1
addx 2
addx -37
addx 1
addx 3
noop
addx 15
addx -21
addx 22
addx -6
addx 1
noop
addx 2
addx 1
noop
addx -10
noop
noop
addx 20
addx 1
addx 2
addx 2
addx -6
addx -11
noop
noop
noop
"""

example_first_star_checkpoints = {
    20: 420,
    60: 1140,
    100: 1800,
    140: 2940,
    180: 2880,
    220: 3960,
}
example_first_star_output = 13140

example_second_star_output = """\
##..##..##..##..##..##..##..##..##..##..
###...###...###...###...###...###...###.
####....####....####....####....####....
#####.....#####.....#####.....#####.....
######......######......######......####
#######.......#######.......#######.....
"""


STOP = "stop"
ADDX = "addx"
DEFERRED_ADD = "deferredadd"


def communication_machine_cycles(input_file):
    line_generator = iter(stripped_input_lines(input_file))
    x = 1
    add_in_cycle = -1
    add_this_value = 0
    for cycle_number in itertools.count(start=1):
        if add_in_cycle is cycle_number:
            op = DEFERRED_ADD
        else:
            op = next(line_generator, STOP)

        if op == STOP:
            break

        if op.startswith(ADDX):
            add_in_cycle = cycle_number + 1
            add_this_value = int(op.split()[-1])

        yield cycle_number, x

        if op.startswith(DEFERRED_ADD):
            x += add_this_value


def first_star(input_file, checkpoints=None):
    cycle_numbers_to_sum = tuple(range(20, 220 + 1, 40))
    signal_strength_sum = 0

    for cycle_number, x in communication_machine_cycles(input_file):
        if cycle_number in cycle_numbers_to_sum:
            signal_strength_sum += x * cycle_number
        if checkpoints and cycle_number in checkpoints:
            assert x * cycle_number == checkpoints[cycle_number]
    return signal_strength_sum


def second_star(input_file):
    output = ""
    for cycle_number, x in communication_machine_cycles(input_file):
        sprite_positions = (x - 1, x, x + 1)
        pixel_number = (cycle_number - 1) % 40
        output += "#" if pixel_number in sprite_positions else "."
        output += "" if cycle_number % 40 else "\n"

    return output


ASCII_ALPHABET = {
    ".##.\n#..#\n#..#\n####\n#..#\n#..#": "A",
    "###.\n#..#\n###.\n#..#\n#..#\n###.": "B",
    ".##.\n#..#\n#...\n#...\n#..#\n.##.": "C",
    "####\n#...\n###.\n#...\n#...\n####": "E",
    "####\n#...\n###.\n#...\n#...\n#...": "F",
    ".##.\n#..#\n#...\n#.##\n#..#\n.###": "G",
    "#..#\n#..#\n####\n#..#\n#..#\n#..#": "H",
    ".###\n..#.\n..#.\n..#.\n..#.\n.###": "I",
    "..##\n...#\n...#\n...#\n#..#\n.##.": "J",
    "#..#\n#.#.\n##..\n#.#.\n#.#.\n#..#": "K",
    "#...\n#...\n#...\n#...\n#...\n####": "L",
    ".##.\n#..#\n#..#\n#..#\n#..#\n.##.": "O",
    "###.\n#..#\n#..#\n###.\n#...\n#...": "P",
    "###.\n#..#\n#..#\n###.\n#.#.\n#..#": "R",
    ".###\n#...\n#...\n.##.\n...#\n###.": "S",
    "#..#\n#..#\n#..#\n#..#\n#..#\n.##.": "U",
    "#...\n#...\n.#.#\n..#.\n..#.\n..#.": "Y",
    "####\n...#\n..#.\n.#..\n#...\n####": "Z",
}

ASCII_ALPHABET_LETTER_HEIGHT = 6
ASCII_ALPHABET_LETTER_WIDTH = 4


def ascii_art_to_string(ascii_art):
    lines = ascii_art.splitlines()
    assert len(lines) == 6
    line_lengths = {len(line) for line in lines}
    assert len(line_lengths) == 1  # all same length
    num_letters = (len(lines[0]) + 1) // (ASCII_ALPHABET_LETTER_WIDTH + 1)
    letters = []
    for letter_number in range(num_letters):
        start = letter_number * (ASCII_ALPHABET_LETTER_WIDTH + 1)
        end = start + ASCII_ALPHABET_LETTER_WIDTH
        letters.append("\n".join(line[start:end] for line in lines))
    return "".join(ASCII_ALPHABET[letter] for letter in letters)


test_ascii_art = """\
####.#..#.###..####.###....##..##..#....
#....#..#.#..#....#.#..#....#.#..#.#....
###..####.#..#...#..#..#....#.#....#....
#....#..#.###...#...###.....#.#.##.#....
#....#..#.#....#....#....#..#.#..#.#....
####.#..#.#....####.#.....##...###.####.
"""


def test_ascii_art_to_string():
    assert ascii_art_to_string(test_ascii_art) == "EHPZPJGL"


def main():
    input_path = pathlib.Path("input", pathlib.Path(__file__).name).with_suffix(".txt")

    print(f"First star answer: {first_star(input_path.open())}")
    second_star_output_ascii = second_star(input_path.open())
    second_star_output = ascii_art_to_string(second_star_output_ascii)
    print(f"Second star answer: {second_star_output}")


@pytest.fixture
def example_input():
    return io.StringIO(example_input_string)


def test_first_star(example_input):
    assert (
        first_star(example_input, example_first_star_checkpoints)
        == example_first_star_output
    )


def test_second_star(example_input):
    assert second_star(example_input) == example_second_star_output


def test_main():
    main()


def stripped_input_lines(input_file):
    return (line.strip() for line in input_file)


if __name__ == "__main__":
    main()
