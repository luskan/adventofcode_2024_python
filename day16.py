from common import run_tests, run_day, verify_result
from typing import List, Tuple, Dict, Optional
import heapq

# Class to hold parsed data
class ParsedData:
    __slots__ = ["grid", "start", "end"]

    def __init__(self):
        self.grid: List[List[str]] = []
        self.start: Tuple[int, int] = (-1, -1)
        self.end: Tuple[int, int] = (-1, -1)

def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    lines = data.strip().split('\n')
    for y, line in enumerate(lines):
        row = list(line)
        for x, char in enumerate(row):
            if char == 'S':
                result.start = (x, y)
            elif char == 'E':
                result.end = (x, y)
        result.grid.append(row)
    return result

def part1(data: ParsedData) -> int:
    return solver(data, track_paths=False)

def part2(data: ParsedData) -> int:
    return solver(data, track_paths=True)

def solver(data: ParsedData, track_paths: bool) -> int:
    grid = data.grid
    start = data.start
    end = data.end

    # Movements: E, S, W, N
    moves = [(1,0), (0,1), (-1,0), (0,-1)]

    # Initialize priority queue
    heap = []
    initial_path = [start] if track_paths else None
    heapq.heappush(heap, (0, start[0], start[1], 0, initial_path))  # (cost, x, y, direction, path)

    # Visited states: (x, y, direction) -> cost
    visited: Dict[Tuple[int, int, int], int] = {}

    min_cost_to_end: Optional[int] = None
    tiles_on_paths: Dict[int, set[Tuple[int, int]]] = {}

    grid_width = len(grid[0])
    grid_height = len(grid)

    while heap:
        cost, x, y, direction, path = heapq.heappop(heap)
        state = (x, y, direction)

        # If we've already visited this state with a lower cost, skip
        if state in visited:
            if visited[state] < cost:
                continue
            elif visited[state] == cost and not track_paths:
                continue  # For Part 1, no need to process equal cost states
        else:
            visited[state] = cost

        # Check if we've reached the end
        if (x, y) == end:
            if not track_paths:
                return cost

            if min_cost_to_end is None:
                min_cost_to_end = cost
            if cost <= min_cost_to_end:
                if path:
                    for tile in path:
                        tiles_on_paths.setdefault(cost, set()).add(tile)

        # If we've found the minimal cost to end and current state's cost exceeds it, terminate
        if min_cost_to_end is not None and cost > min_cost_to_end:
            break

        # Move forward
        dx, dy = moves[direction]
        nx, ny = x + dx, y + dy
        if 0 <= ny < grid_height and 0 <= nx < grid_width:
            if grid[ny][nx] != '#':
                new_state = (nx, ny, direction)
                new_cost = cost + 1
                if new_state not in visited or visited[new_state] >= new_cost:
                    new_path = path + [(nx, ny)] if track_paths else None
                    heapq.heappush(heap, (new_cost, nx, ny, direction, new_path))

        # Rotate clockwise
        new_dir_cw = (direction + 1) % 4
        new_state_cw = (x, y, new_dir_cw)
        new_cost_cw = cost + 1000
        if new_state_cw not in visited or visited[new_state_cw] >= new_cost_cw:
            heapq.heappush(heap, (new_cost_cw, x, y, new_dir_cw, path))

        # Rotate counterclockwise
        new_dir_ccw = (direction - 1) % 4
        new_state_ccw = (x, y, new_dir_ccw)
        new_cost_ccw = cost + 1000
        if new_state_ccw not in visited or visited[new_state_ccw] >= new_cost_ccw:
            heapq.heappush(heap, (new_cost_ccw, x, y, new_dir_ccw, path))

    if not track_paths:
        # Part 1: minimal cost found and returned earlier
        raise ValueError("No valid path found from start to end")

    # Part 2: Collect all tiles on any minimal cost path
    return len(tiles_on_paths.get(min_cost_to_end, set()))

def print_grid_with_path(grid: List[List[str]], path: set[Tuple[int, int]]) -> None:
    grid_copy = [row[:] for row in grid]
    for x, y in path:
        if grid_copy[y][x] not in ('S', 'E'):
            grid_copy[y][x] = '\033[91m*\033[0m'
    for row in grid_copy:
        print(''.join(row))

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part: int) -> bool:
    test_input1 = """
###############
#.......#....E#
#.#.###.#.###.#
#.....#.#...#.#
#.###.#####.#.#
#.#.#.......#.#
#.#.#####.###.#
#...........#.#
###.#.#####.#.#
#...#.....#.#.#
#.#.#.###.#.#.#
#.....#...#.#.#
#.###.#.#.#.#.#
#S..#.....#...#
###############
    """

    expected_part1_1 = 7036
    expected_part2_1 = 45

    # Example 2
    test_input2 = """
#################
#...#...#...#..E#
#.#.#.#.#.#.#.#.#
#.#.#.#...#...#.#
#.#.#.#.###.#.#.#
#...#.#.#.....#.#
#.#.#.#.#.#####.#
#.#...#.#.#.....#
#.#.#####.#.###.#
#.#.#.......#...#
#.#.###.#####.###
#.#.#...#.....#.#
#.#.#.#####.###.#
#.#.#.........#.#
#.#.#.#########.#
#S#.............#
#################
    """

    expected_part1_2 = 11048
    expected_part2_2 = 64

    tests = [
        (test_input1, expected_part1_1, expected_part2_1),
        (test_input2, expected_part1_2, expected_part2_2),
    ]

    print()
    all_pass = True
    for i, (input_data, expected1, expected2) in enumerate(tests, 1):
        parsed_data = parse_input(input_data)
        result1 = part1(parsed_data)
        result2 = part2(parsed_data)

        all_pass = all_pass and verify_result(result1, expected1, 1)
        all_pass = all_pass and verify_result(result2, expected2, 2)
    return all_pass

if __name__ == "__main__":
    run_tests(16)
    run_day(16, part1=True, part2=True)
