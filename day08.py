from typing import List, Tuple
from collections import defaultdict

from common import verify_result, run_day, run_tests
from functools import cmp_to_key

Point = tuple[int, int]

class ParsedData:
    __slots__ = ["line", "towers", "width", "height"]

    def __init__(self):
        self.line: str = ""
        self.towers: dict[str, List[Point]] = {}
        self.width: int = 0
        self.height: int = 0

def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    for line in data.split('\n'):
        if line.strip():
            #map each char to result.towers
            for i, ch in enumerate(line):
                if ch != '.':
                    if ch not in result.towers:
                        result.towers[ch] = []
                    result.towers[ch].append((i, result.height))
            result.width = len(line)
            result.height += 1
    result.line = data
    return result

def part1(data: ParsedData) -> int:
    return solver(data, 1)

def solver(data: ParsedData, part: int) -> int:


    antinodes: dict[str, set[Point]] = {}
    for key, tower in data.towers.items():
        #print(f"key: {key}, tower: {tower}")
        for i in range(len(tower)):
            for j in range(len(tower)):
                if i == j:
                    continue
                x1, y1 = tower[i]
                x2, y2 = tower[j]

                for d in range(1 if part == 1 else 0, 100):
                    a_x = (x2 - x1) * (2 if part == 1 else 1) * d + x1
                    a_y = (y2 - y1) * (2 if part == 1 else 1) * d + y1
                    if a_x < 0 or a_x >= data.width or a_y < 0 or a_y >= data.height:
                        break
                    if key not in antinodes:
                        antinodes[key] = set[tuple[int, int]]()
                    antinodes[key].add((a_x, a_y))
                    if part == 1:
                        break

    all_ants = set[tuple[int,int]]()
    for ants in antinodes.values():
        all_ants.update(ants)
    return len(all_ants)

def part2(data: ParsedData) -> int:
    return solver(data, 2)

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> None:
    test_input = """
............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    # Test part 1
    if (part == 1):
        all_pass = all_pass and verify_result(part1(parsed_data), 14, 1)

    # Test part 2
    if (part == 2):
        all_pass = all_pass and verify_result(part2(parsed_data), 34, 2)

    return all_pass

if __name__ == "__main__":
    run_tests(8)
    run_day(8, part1=True, part2=True)
