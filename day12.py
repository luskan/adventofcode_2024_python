from typing import List, Tuple
from collections import defaultdict, deque

from common import verify_result, run_day, run_tests
from functools import cmp_to_key


# Class
class ParsedData:
    __slots__ = ["line"]

    def __init__(self):
        self.line: str = ""


def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    result.line = data
    return result


def solver(data: ParsedData, part: int) -> int:
    # Split the input into a grid of characters
    grid = [list(line) for line in data.line.strip().split('\n') if line]
    if not grid:
        return 0
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    total = 0

    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(rows):
        for c in range(cols):
            if not visited[r][c]:
                plant_type = grid[r][c]
                # Initialize BFS
                queue = deque()
                queue.append((r, c))
                visited[r][c] = True
                area = 0
                perimeter = 0

                while queue:
                    x, y = queue.popleft()
                    area += 1

                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        # Check if the neighbor is out of bounds
                        if nx < 0 or nx >= rows or ny < 0 or ny >= cols:
                            perimeter += 1
                        elif grid[nx][ny] != plant_type:
                            perimeter += 1
                        else:
                            if not visited[nx][ny]:
                                visited[nx][ny] = True
                                queue.append((nx, ny))

                # Calculate the cost for this region
                total += area * perimeter

    return total


def part1(data: ParsedData) -> int:
    return solver(data, 1)


def part2(data: ParsedData) -> int:
    return solver(data, 2)


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test(part) -> None:
    test_cases = [
        {
            'input': """
AAAA
BBCD
BBCC
EEEC
""",
            'expected': 140
        },
        {
            'input': """
OOOOO
OXOXO
OOOOO
OXOXO
OOOOO
""",
            'expected': 772
        },
        {
            'input': """
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
""",
            'expected': 1930
        }
    ]

    all_pass = True

    for idx, case in enumerate(test_cases, 1):
        parsed_data = parse_input(case['input'])
        result = part1(parsed_data)
        expected = case['expected']
        if not verify_result(result, expected, part):
            print(f"Test case {idx} failed for part {part}: got {result}, expected {expected}")
            all_pass = False
        else:
            print(f"Test case {idx} passed for part {part}.")

    if all_pass:
        print("All test cases passed!")
    else:
        print("Some test cases failed.")

if __name__ == "__main__":
    run_tests(12)
    run_day(12, part1=True, part2=True)
