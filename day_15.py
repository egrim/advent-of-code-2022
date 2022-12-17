import io
import multiprocessing
import os
import pathlib
import queue
import re
from collections import defaultdict
from dataclasses import dataclass

import itertools
import pytest

UNDEFINED = object()

example_input_string = """\
Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3
"""

example_first_star_output = 26
example_second_star_output = 56000011

SENSOR_READING = re.compile(
    r"Sensor at x=(?P<x>-?\d+), y=(?P<y>-?\d+): closest beacon is at x=(?P<beacon_x>-?\d+), y=(?P<beacon_y>-?\d+)"
)
X = 0
Y = 1


@dataclass(frozen=True)
class InclusiveInterval:
    min: int
    max: int

    def __iter__(self):
        yield from iter(range(self.min, self.max + 1))

    def __contains__(self, item):
        return self.min <= item <= self.max

    def size(self):
        return self.max - self.min + 1


class InclusiveIntervalSet:
    def __init__(self, iterable=None):
        self.intervals = []
        if iterable:
            for interval in iterable:
                self.add(interval)

    def add(self, new_interval):
        new_intervals = []
        for index, interval in enumerate(self.intervals):
            if new_interval.max < interval.min - 1:  # completely before, finished
                new_intervals.append(new_interval)
                new_intervals.extend(self.intervals[index:])
                break
            elif interval.max < new_interval.min - 1:  # completely after, iterate
                new_intervals.append(interval)
            else:  # merge needed for contiguous/overlapping intevals
                merged_interval = InclusiveInterval(
                    min(interval.min, new_interval.min),
                    max(interval.max, new_interval.max),
                )
                if new_interval.max < interval.max:
                    new_intervals.append(merged_interval)
                    new_intervals.extend(self.intervals[index + 1 :])
                    break
                else:
                    new_interval = merged_interval  # setup next iteration to check for further merging
        else:
            new_intervals.append(new_interval)
        self.intervals = new_intervals

    def remove(self, remove_interval):
        new_intervals = []
        for index, interval in enumerate(self.intervals):
            if remove_interval.max < interval.min:  # completely before, finished
                new_intervals.extend(self.intervals[index:])
                break
            elif interval.max < remove_interval.min:  # completely after, iterate
                pass
            else:  # some removal necessary
                if interval.min < remove_interval.min:
                    new_intervals.append(
                        InclusiveInterval(interval.min, remove_interval.min - 1)
                    )
                if remove_interval.max < interval.max:
                    new_intervals.append(
                        InclusiveInterval(remove_interval.max + 1, interval.max)
                    )
                    new_intervals.extend(self.intervals[index + 1 :])
                    break
        self.intervals = new_intervals

    def size(self):
        return sum(interval.size() for interval in self.intervals)

    def first_gap(self, within_interval):
        if within_interval.min > self.intervals[-1].max:
            return within_interval.min

        for interval in self.intervals:
            if within_interval.min < interval.min:
                return within_interval.min
            if within_interval.min in interval:
                if interval.max + 1 in within_interval:
                    return interval.max + 1
                else:
                    return None


@dataclass
class Sensor:
    x: int
    y: int

    beacon_x: int
    beacon_y: int

    sensor_to_beacon_distance: int = None

    def __post_init__(self):
        sensor_x, sensor_y = self.x, self.y
        beacon_x, beacon_y = self.beacon_x, self.beacon_y
        sensor_to_beacon_distance = abs(sensor_x - beacon_x) + abs(sensor_y - beacon_y)
        self.exclusion_y_interval = InclusiveInterval(
            self.y - sensor_to_beacon_distance, self.y + sensor_to_beacon_distance
        )
        self.sensor_to_beacon_distance = sensor_to_beacon_distance

    def get_x_exclusion_interval(self, y):
        if y not in self.exclusion_y_interval:
            return None

        sensor_x, sensor_y = self.x, self.y
        spread = self.sensor_to_beacon_distance - abs(sensor_y - y)
        return InclusiveInterval(sensor_x - spread, sensor_x + spread)


class Space:
    def __init__(self, input_file):
        sensors = []

        for line in stripped_input_lines(input_file):
            if match := SENSOR_READING.match(line):
                x, y = int(match["x"]), int(match["y"])
                beacon_x, beacon_y = int(match["beacon_x"]), int(match["beacon_y"])
                sensor = Sensor(x, y, beacon_x, beacon_y)
                sensors.append(sensor)

        self.sensors = sensors

    def get_x_exclusion_interval_set(self, y, exclude_beacons=False):
        intervals = InclusiveIntervalSet()
        beacons_to_remove_from_exclusions = set()
        for sensor in self.get_sensors_affecting_y(y):
            intervals.add(sensor.get_x_exclusion_interval(y))
            if exclude_beacons and sensor.beacon_y == y:
                beacons_to_remove_from_exclusions.add(sensor.beacon_x)

        for beacon_x_position in beacons_to_remove_from_exclusions:
            intervals.remove(InclusiveInterval(beacon_x_position, beacon_x_position))

        return intervals

    def get_sensors_affecting_y(self, y):
        sensors = [
            sensor for sensor in self.sensors if y in sensor.exclusion_y_interval
        ]
        return sensors


def first_star(input_file, row_number=2000000):
    space = Space(input_file)
    exclusions = space.get_x_exclusion_interval_set(row_number, exclude_beacons=True)
    return exclusions.size()


def gap_checker(space, range_max, y_start, y_stop, result_queue):
    search_space = InclusiveInterval(0, range_max)
    for y in range(y_start, y_stop):
        if not result_queue.empty():
            break

        interval_set = space.get_x_exclusion_interval_set(y)
        if (x := interval_set.first_gap(search_space)) is not None:
            result_queue.put((x, y))


def second_star(input_file, range_max=4000000):
    space = Space(input_file)

    num_processes = os.cpu_count() or 1
    chunk_size = range_max // num_processes
    result_queue = multiprocessing.Queue()
    processes = []
    for i in range(num_processes):
        y_start = i * chunk_size
        if i == num_processes - 1:
            y_stop = range_max
        else:
            y_stop = (i + 1) * chunk_size

        process = multiprocessing.Process(
            target=gap_checker,
            args=(space, range_max, y_start, y_stop, result_queue),
        )
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    if result_queue.empty():
        raise ValueError("no solution found!")

    x, y = result_queue.get()
    return 4000000 * x + y


# noinspection DuplicatedCode
def main():
    input_path = pathlib.Path("input", pathlib.Path(__file__).name).with_suffix(".txt")

    print(f"First star answer: {first_star(input_path.open())}")
    print(f"Second star answer: {second_star(input_path.open())}")


@pytest.fixture
def example_input():
    return io.StringIO(example_input_string)


def test_first_star(example_input):
    assert first_star(example_input, 10) == example_first_star_output


def test_second_star(example_input):
    assert second_star(example_input, 20) == example_second_star_output


def test_main():
    main()


def stripped_input_lines(input_file):
    return (line.strip() for line in input_file)


if __name__ == "__main__":
    main()
