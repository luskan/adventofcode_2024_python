from math import log10
from typing import List, Tuple
from collections import defaultdict

from common import verify_result, run_day, run_tests
from functools import cmp_to_key
from concurrent.futures import ProcessPoolExecutor

#Point = Tuple[int, int]
class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


class ParsedData:
    Grid = List[List[int]]
    StartPoint = Point

    def __init__(self):
        self.grid: ParsedData.Grid = []
        self.start_point: ParsedData.StartPoint = Point(0, 0)

GRID_WALL = 2
GRID_EMPTY = 1
GRID_GUARD = 0

def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    for line in data.split('\n'):
        if line.strip():
            line_list = [GRID_WALL if char == '#' else GRID_EMPTY if char == '.' else GRID_GUARD for char in line]
            result.grid.append(line_list)

            caret_ind = line.find("^")
            if caret_ind != -1:
                result.start_point = Point(caret_ind, len(result.grid) - 1)

    return result

class SimulationResults:
    def __init__(self):
        self.visited: List[Point] = []
        self.visited_set: set[Point] = set()
        self.end_point: Point = Point(-1, -1)
        self.loop = False

def simulateGuardWalking(data: ParsedData, max_width: int, max_height: int, extra_obstacle: Point, collect_visited: bool,
                         results: SimulationResults, turn_points):
    current_pos = Point(data.start_point.x, data.start_point.y)
    current_dir = Point(0, -1)

    if collect_visited:
        results.visited.append(Point(current_pos.x, current_pos.y))
        results.visited_set.add(Point(current_pos.x, current_pos.y))
    if turn_points is not None:
        turn_points.clear()

    results.loop = False

    #create list of specified size initialized to False

    while True:
        current_pos.x = current_pos.x + current_dir.x
        current_pos.y = current_pos.y + current_dir.y

        #if current_pos is out of bounds, break
        if current_pos.x < 0 or current_pos.x >= max_width or current_pos.y < 0 or current_pos.y >= max_height:
            results.end_point = current_pos
            results.loop = False
            break

        if data.grid[current_pos.y][current_pos.x] == GRID_WALL or current_pos == extra_obstacle:
            current_pos.x = current_pos.x - current_dir.x
            current_pos.y = current_pos.y - current_dir.y

            if turn_points is not None:
                turn_id = (current_pos.x, current_pos.y, current_dir.x, current_dir.y)
                if turn_id in turn_points:
                    results.loop = True
                    break
                turn_points.add(turn_id)

            tmp = current_dir.x
            current_dir.x = -current_dir.y
            current_dir.y = tmp

        #mark as visited
        if collect_visited:
            results.visited.append(Point(current_pos.x, current_pos.y))
            results.visited_set.add(Point(current_pos.x, current_pos.y))


def part1(data: ParsedData) -> int:
    results = SimulationResults()
    max_width = len(data.grid[0])
    max_height = len(data.grid)
    simulateGuardWalking(data, max_width, max_height, Point(-1, -1), True, results, None)
    return len(results.visited_set)


    # Function to process a range of points
def process_range_of_points(start: int, end: int, data: ParsedData, max_width: int, max_height: int, visited_list: List[Point]) -> int:
    turn_points: set[Tuple[int, int, int, int]] = set()
    tested_obstacles = set[Point]()
    local_valid_moves = 0
    results = SimulationResults()
    for i in range(start, end):
        point = visited_list[i]
        if data.start_point == point:
            continue
        if point in tested_obstacles:
            continue

        tested_obstacles.add(point)
        #print(f"[{start}, {end}]Testing obstacle at {point}")
        simulateGuardWalking(data, max_width, max_height, point, False, results, turn_points)
        if results.loop:
            local_valid_moves += 1
    return local_valid_moves


def process_range_wrapper(args):
    start, end, data, max_width, max_height, visited_list = args
    return process_range_of_points(start, end, data, max_width, max_height, visited_list)


def part2(data: ParsedData, num_processes: int = 4) -> int:
    initial_results = SimulationResults()
    max_width = len(data.grid[0])
    max_height = len(data.grid)
    simulateGuardWalking(data, max_width, max_height, Point(-1, -1), True, initial_results, None)

    valid_moves = 0
    visited_list = list(initial_results.visited_set)

    # Divide work among processes
    num_points = len(visited_list)
    step = (num_points + num_processes - 1) // num_processes  # Calculate the range per process
    ranges = [(i, min(i + step, num_points)) for i in range(0, num_points, step)]

    # Run threads with the defined ranges
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        results = executor.map(
            process_range_wrapper,
            [(r[0], r[1], data, max_width, max_height, visited_list) for r in ranges]
        )

    valid_moves = sum(results)

    return valid_moves


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test(part) -> None:
    test_input = """
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    # Test part 1
    if (part == 1):
        all_pass = all_pass and verify_result(part1(parsed_data), 41, 1)

    # Test part 2
    if (part == 2):
        all_pass = all_pass and verify_result(part2(parsed_data), 6, 2)

    return all_pass

if __name__ == "__main__":
    #run_tests(6)
    run_day(6, part1=False, part2=True)
