import io
import pathlib

import pytest


example_input_string = """
"""

example_first_star_output = None
example_second_star_output = None


def first_star(input_file):
    return input_file


def second_star(input_file):
    return input_file


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


if __name__ == "__main__":
    main()
