import io
import pathlib

import pytest

example_input_string = """
1000
2000
3000

4000

5000
6000

7000
8000
9000

10000
"""

example_first_star_output = 24000
example_second_star_output = 45000


def first_star(input_file):
    return top_calorie_counts(input_file, 1)


def second_star(input_file):
    return top_calorie_counts(input_file, 3)


def main():
    input_path = pathlib.Path("input", pathlib.Path(__file__).name).with_suffix(".txt")

    print(f"First star answer: {first_star(input_path.open())}")
    print(f"Second star answer: {second_star(input_path.open())}")


def stream_of_calorie_totals(input_file):
    with input_file as in_file:
        current_elf_calories = 0
        for line in in_file:
            line = line.strip()
            if line:
                line_calories = int(line)
                current_elf_calories += line_calories
            else:
                yield current_elf_calories
                current_elf_calories = 0
        else:
            yield current_elf_calories


def top_calorie_counts(input_file, count):
    top_calories = [0] * count
    for calories in stream_of_calorie_totals(input_file):
        if calories > top_calories[0]:
            top_calories.append(calories)
            top_calories.sort()
            top_calories.pop(0)

    return sum(top_calories)


@pytest.fixture
def test_input():
    return io.StringIO(example_input_string)


def test_first_star(test_input):
    assert example_first_star_output == first_star(test_input)


def test_second_star(test_input):
    assert example_second_star_output == second_star(test_input)


if __name__ == "__main__":
    main()
