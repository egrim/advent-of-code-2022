import functools
import io
import operator
import pathlib
import typing
from dataclasses import dataclass, field

import pytest

example_input_string = """\
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
"""

example_first_star_output = 10605
example_second_star_output = 2713310158


@dataclass
class Monkey:
    items: list[int]
    operation: typing.Callable[[int], int]
    test_divisor: int
    lookup_target: typing.Callable[[int], int]
    inspections: int = 0


def build_monkey(line_generator):
    assert next(line_generator).startswith("Monkey")
    items_str = next(line_generator).split(": ")[-1]
    items = list(map(int, items_str.split(", ")))

    operation_str = next(line_generator).split("= ")[-1]
    if "*" in operation_str:
        op = operator.mul
    elif "+" in operation_str:
        op = operator.add
    else:
        raise ValueError

    operand = operation_str.split(" ")[-1]
    if operand != "old":
        operand = int(operand)

    def operation(old):
        if operand == "old":
            return op(old, old)
        else:
            return op(old, operand)

    test_divisor = int(next(line_generator).split("divisible by ")[-1])
    target_if_true, target_if_false = tuple(
        int(next(line_generator).split("throw to monkey ")[-1]) for _ in range(2)
    )

    def lookup_target(value):
        if value % test_divisor == 0:
            return target_if_true
        else:
            return target_if_false

    return Monkey(items, operation, test_divisor, lookup_target)


def parse_monkey_state_file(input_file):
    line_generator = iter(stripped_input_lines(input_file))
    monkeys = []
    while True:
        monkeys.append(build_monkey(line_generator))

        try:
            next(line_generator)
        except StopIteration:
            break

    return monkeys


def first_star(input_file):
    monkeys = parse_monkey_state_file(input_file)
    for round_number in range(20):
        for monkey in monkeys:
            for item in monkey.items:
                new_value = monkey.operation(item)
                new_value //= 3
                throw_to = monkey.lookup_target(new_value)
                monkeys[throw_to].items.append(new_value)
                monkey.inspections += 1

            monkey.items = []

    inspections = sorted(monkey.inspections for monkey in monkeys)
    return inspections[-1] * inspections[-2]


def second_star(input_file):
    monkeys = parse_monkey_state_file(input_file)
    max_factor = functools.reduce(
        operator.mul, (monkey.test_divisor for monkey in monkeys)
    )
    for round_number in range(10000):
        for monkey in monkeys:
            for item in monkey.items:
                new_value = monkey.operation(item)
                new_value %= max_factor
                throw_to = monkey.lookup_target(new_value)
                monkeys[throw_to].items.append(new_value)
                monkey.inspections += 1

            monkey.items = []

    inspections = sorted(monkey.inspections for monkey in monkeys)
    return inspections[-1] * inspections[-2]


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
