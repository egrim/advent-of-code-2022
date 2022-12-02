import functools
import io
import pathlib
from enum import Enum

import pytest

example_input_string = """
A Y
B X
C Z
"""

example_first_star_output = 15
example_second_star_output = 12


@functools.total_ordering
class RoShamBo(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    A = ROCK
    B = PAPER
    C = SCISSORS

    X = ROCK
    Y = PAPER
    Z = SCISSORS

    def __lt__(self, other):
        return self.get_winner() == other

    def get_winner(self):
        match self:
            case self.ROCK:
                return self.PAPER
            case self.PAPER:
                return self.SCISSORS
            case self.SCISSORS:
                return self.ROCK

    def get_loser(self):
        match self:
            case self.ROCK:
                return self.SCISSORS
            case self.PAPER:
                return self.ROCK
            case self.SCISSORS:
                return self.PAPER


def test_roshambo():
    rock = RoShamBo.ROCK
    paper = RoShamBo.PAPER
    scissors = RoShamBo.SCISSORS

    assert RoShamBo['A'] == RoShamBo.ROCK
    assert RoShamBo['B'] == RoShamBo.PAPER
    assert RoShamBo['C'] == RoShamBo.SCISSORS

    assert RoShamBo['X'] == RoShamBo.ROCK
    assert RoShamBo['Y'] == RoShamBo.PAPER
    assert RoShamBo['Z'] == RoShamBo.SCISSORS

    assert rock == rock
    assert rock > scissors
    assert rock < paper
    assert paper < scissors
    assert scissors < rock


def first_star(input_file):
    score = 0
    for line in input_file:
        line = line.strip()
        if line:
            first, second = line.split()
            them = RoShamBo[first]
            me = RoShamBo[second]
            score += me.value
            if me == them:
                score += 3
            elif me > them:
                score += 6

    return score


def second_star(input_file):
    score = 0
    for line in input_file:
        line = line.strip()
        if line:
            first, second = line.split()
            them = RoShamBo[first]
            match second:
                case 'X':  # lose
                    me = them.get_loser()
                case 'Y':  # draw
                    me = them
                case 'Z':  # win
                    me = them.get_winner()
                case _:
                    raise ValueError

            score += me.value
            if me == them:
                score += 3
            elif me > them:
                score += 6

    return score


def main():
    input_path = pathlib.Path("input", pathlib.Path(__file__).name).with_suffix(".txt")

    print(f"First star answer: {first_star(input_path.open())}")
    print(f"Second star answer: {second_star(input_path.open())}")


@pytest.fixture
def test_input():
    return io.StringIO(example_input_string)


def test_first_star(test_input):
    assert example_first_star_output == first_star(test_input)


def test_second_star(test_input):
    assert example_second_star_output == second_star(test_input)


if __name__ == '__main__':
    main()
