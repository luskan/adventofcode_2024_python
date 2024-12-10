from typing import List, Tuple
from collections import defaultdict

from common import verify_result
from functools import cmp_to_key

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
    Grid = List[str]
    StartPoint = Point

    def __init__(self):
        self.grid: ParsedData.Grid = []
        self.start_point: ParsedData.StartPoint = Point(0, 0)


def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    for line in data.split('\n'):
        if line.strip():
            result.grid.append(line)

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

turn_points: set[Tuple[Point, Point]] = set()
def simulateGuardWalking(data: ParsedData, extra_obstacle: Point, collect_visited: bool, results: SimulationResults):
    current_pos = Point(data.start_point.x, data.start_point.y)
    current_dir = Point(0, -1)

    if collect_visited:
        results.visited.append(current_pos)
        results.visited_set.add(current_pos)
    turn_points.clear()
    results.loop = False

    while True:
        current_pos = Point(current_pos.x + current_dir.x, current_pos.y + current_dir.y)

        #if current_pos is out of bounds, break
        if current_pos.x < 0 or current_pos.x >= len(data.grid[0]) or current_pos.y < 0 or current_pos.y >= len(data.grid):
            results.end_point = current_pos
            results.loop = False
            break

        if data.grid[current_pos.y][current_pos.x] == "#" or current_pos == extra_obstacle:
            current_pos = Point(current_pos.x - current_dir.x, current_pos.y - current_dir.y)

            if turn_points.__contains__((current_pos, current_dir)):
                results.loop = True
                break
            turn_points.add((current_pos, current_dir))

            #rotate current_dir right 90 degrees
            current_dir = Point(-current_dir.y, current_dir.x)

        #mark as visited
        if collect_visited:
            results.visited.append(current_pos)
            results.visited_set.add(current_pos)

def part1(data: ParsedData) -> int:
    results = SimulationResults()
    simulateGuardWalking(data, Point(-1, -1), True, results)
    return len(results.visited_set)

def part2(data: ParsedData) -> int:
    initial_results = SimulationResults()
    simulateGuardWalking(data, Point(-1, -1), True, initial_results)

    valid_moves = 0
    results = SimulationResults()

    #tested_obstacles = set[Point]()
    for point in initial_results.visited_set:
        if data.start_point == point:
            continue
        #if tested_obstacles.__contains__(point):
        #    continue
        #tested_obstacles.add(point)

        simulateGuardWalking(data, point, False, results)
        if results.loop:
            valid_moves += 1

    return valid_moves


def print_grid(data: ParsedData, visited: set[Point], current_pos: Point) -> None:
    for y in range(len(data.grid)):
        for x in range(len(data.grid[0])):
            if (x, y) == current_pos:
                print("^", end="")
            else:
                if visited.__contains__((x, y)):
                    print("X", end="")
                elif data.grid[y][x] == "^":
                    print(".", end="")
                else:
                    print(data.grid[y][x], end="")
        print()
        print()


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test() -> None:
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

    # Test part 1
    verify_result(part1(parsed_data), 41, 1)
    print("Part 1 tests passed!")

    # Test part 2
    verify_result(part2(parsed_data), 6, 2)
    print("Part 2 tests passed!")
