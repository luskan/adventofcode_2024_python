import sys
from typing import List, Tuple
from collections import deque

from common import verify_result, run_day, run_tests


class ParsedData:
    def __init__(self):
        self.positions: List[Tuple[int, int]] = []


def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    lines = data.strip().splitlines()
    for line in lines:
        if line.strip():
            parts = line.strip().split(',')
            if len(parts) != 2:
                continue
            try:
                x, y = int(parts[0]), int(parts[1])
                result.positions.append((x, y))
            except ValueError:
                continue
    return result


def part1(data: ParsedData, grid_size: int, max_bytes: int) -> int:
    return solver(data, grid_size, max_bytes, 1)


def solver(data: ParsedData, grid_size: int, max_bytes: int, part: int) -> int:
    # Simulate falling bytes
    corrupted = set()
    for i in range(min(max_bytes, len(data.positions))):
        x, y = data.positions[i]
        if 0 <= x <= grid_size and 0 <= y <= grid_size:
            corrupted.add((x, y))

    # start,end
    start = (0, 0)
    end = (grid_size, grid_size)

    # BFS initialization
    queue = deque()
    queue.append((start, 0))  # (position, steps)
    visited = set()
    visited.add(start)

    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Find path
    while queue:
        current, steps = queue.popleft()
        if current == end:
            return steps  # Found the shortest path

        x, y = current
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            if 0 <= nx <= grid_size and 0 <= ny <= grid_size:
                if neighbor not in corrupted and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, steps + 1))

    return -1  # No path found


def part2(data: ParsedData, grid_size: int, max_bytes: int) -> str:
    # Find the blocking byte using binary search
    left: int = 0
    right: int = len(data.positions)
    while left < right:
        mid = left + (right - left) // 2
        res = solver(data, grid_size, mid, 2)
        if res == -1:
            right = mid
        else:
            left = mid+1

    return f"{data.positions[left-1][0]},{data.positions[left-1][1]}"



def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data, 70, 1024) if part == 1 else part2(parsed_data, 70, sys.maxsize)

    result = solve(test_input, part=1)
    print(f"Minimum number of steps: {result}")


def test(part) -> bool:
    test_input = """
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    # Test part 1
    if (part == 1):
        all_pass = all_pass and verify_result(part1(parsed_data, 6, 12), 22, 1)

    # Test part 2
    if (part == 2):
        all_pass = all_pass and verify_result(part2(parsed_data, 6, 12), "6,1", 2)

    return all_pass


if __name__ == "__main__":
    run_tests(18)
    run_day(18, part1=True, part2=True)
