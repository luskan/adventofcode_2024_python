import sys
from collections import deque
from typing import Tuple, List
from common import verify_result, run_day, run_tests

class ParsedData:
    __slots__ = ["codes"]

    def __init__(self):
        self.codes: List[str] = []

def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    result.codes = data.strip().split('\n')
    return result

Point2 = Tuple[int, int]

def is_valid_path(path: List[Point2]) -> bool:
    for i in range(1, len(path)):
        r1, c1 = path[i - 1]
        r2, c2 = path[i]
        if not ((abs(r2 - r1) == 1 and c2 == c1) or (abs(c2 - c1) == 1 and r2 == r1)):
            return False
    return True

def path_to_dirs(path: List[Point2]) -> str:
    if not is_valid_path(path):
        raise ValueError("Invalid path: non-adjacent points detected.")
    dirs = []
    for i in range(1, len(path)):
        r1, c1 = path[i - 1]
        r2, c2 = path[i]
        if r1 == r2:
            if c2 > c1:
                dirs.append('>')
            else:
                dirs.append('<')
        else:
            if r2 > r1:
                dirs.append('v')
            else:
                dirs.append('^')
    return ''.join(dirs)

bfs_cache_dirs = {}
def bfs_all_paths_as_dirs(grid_id: int, grid: List[str], start: Point2, end: Point2) -> List[str]:
    if (grid_id, start, end) in bfs_cache_dirs:
        return bfs_cache_dirs[(grid_id, start, end)]
    paths = bfs_all_paths(grid, start, end)
    paths_dirs: List[str] = []
    for path in paths:
        path_dirs = path_to_dirs(path)
        paths_dirs.append(path_dirs+"A")
    bfs_cache_dirs[(grid_id, start, end)] = paths_dirs
    return paths_dirs

def bfs_all_paths(grid: Tuple[str, ...], start: Point2, end: Point2) -> Tuple[Tuple[Point2, ...], ...]:
    """
    BFS to find all paths from start to end with the minimal length.
    :param grid: a grid map where the path is being found, ex: "789", "456", "123", " 0A"
    :param start: a strt position
    :param end: an end positions
    :return: list of paths of min lenghts
    """

    rows, cols = len(grid), len(grid[0])

    # Initialize the distance grid with infinity
    distances = [[float('inf') for _ in range(cols)] for _ in range(rows)]

    # Initialize the predecessors grid with empty lists
    predecessors: List[List[List[Point2]]] = [[[] for _ in range(cols)] for _ in range(rows)]

    # Initialize the BFS queue
    queue = deque()
    queue.append(start)

    distances[start[0]][start[1]] = 0

    # Define movement directions: Right, Down, Up, Left
    directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]

    while queue:
        current = queue.popleft()
        current_row, current_col = current
        current_distance = distances[current_row][current_col]

        for drow, dcol in directions:
            new_row, new_col = current_row + drow, current_col + dcol
            if 0 <= new_row < rows and 0 <= new_col < cols and grid[new_row][new_col] != ' ':
                new_distance = current_distance + 1
                if new_distance < distances[new_row][new_col]:
                    # Found a shorter path to the neighbor
                    distances[new_row][new_col] = new_distance
                    predecessors[new_row][new_col] = [current]
                    queue.append((new_row, new_col))
                elif new_distance == distances[new_row][new_col]:
                    # Found an alternative path with the same minimal distance
                    predecessors[new_row][new_col].append(current)

    # If the end is unreachable, return an empty tuple
    if distances[end[0]][end[1]] == float('inf'):
        return ()

    # Function to recursively build all paths from end to start
    def build_paths(current: Point2) -> Tuple[Tuple[Point2, ...], ...]:
        if current == start:
            return ((start,),)
        paths = []
        for predecessor in predecessors[current[0]][current[1]]:
            for path in build_paths(predecessor):
                paths.append(path + (current,))
        return tuple(paths)

    all_paths = build_paths(end)
    return all_paths

def find_button_sequence_length(code: str, robots: int) -> int:
    key_pad_grid: List[str] = ["789", "456", "123", " 0A"]
    dir_pad_grid: List[str] = [" ^A", "<v>"]

    key_pad_dict: dict[str, Point2] = {}
    for r, row in enumerate(key_pad_grid):
        for c, key in enumerate(row):
            key_pad_dict[key] = (r, c)

    dir_pad_dict = {}
    for r, row in enumerate(dir_pad_grid):
        for c, key in enumerate(row):
            dir_pad_dict[key] = (r, c)

    pad_last_positions: List[Point2] = [key_pad_dict['A']]
    pad_grids: List[: List[str]] = [key_pad_grid]
    pad_dicts: List[dict[str, Point2]] = [key_pad_dict]
    for i in range(1, robots+1):
        pad_last_positions.append(dir_pad_dict['A'])
        pad_grids.append(dir_pad_grid)
        pad_dicts.append(dir_pad_dict)

    # Its important to not that we dont look for a sequence of moves but its count.
    # The second important thing is to use memoization.
    find_seq_cache = {}
    def find_sequence_len(code_s: str, phase: int) -> int:
        if (code_s, phase) in find_seq_cache:
            return find_seq_cache[(code_s, phase)]
        final_path_len = 0

        # Iterate each code to press
        for cc in code_s:

            # Find a start position (not sure if this is needed, as it always ends at A in previous move)
            c_pos: Point2 = pad_last_positions[phase]
            # Find a new position to press
            new_cpos: Point2 = pad_dicts[phase][cc]

            # Get the paths to new position. There can be many paths of minimal length. We must choose the
            # shortest one after expanding it with the other robots in the queue (after a recursive call).
            paths = bfs_all_paths_as_dirs(0 if phase == 0 else 1, pad_grids[phase], c_pos, new_cpos)

            # Find the shortest path after expanding it with the other robots in the queue
            min_path_len = sys.maxsize
            for path in paths:
                pad_last_positions[phase] = new_cpos
                min_path_len_tmp = len(path)
                if phase < robots:
                    min_path_len_tmp = find_sequence_len(path, phase + 1)
                if min_path_len_tmp < min_path_len:
                    min_path_len = min_path_len_tmp
            final_path_len += min_path_len

        find_seq_cache[(code_s, phase)] = final_path_len
        return final_path_len

    return find_sequence_len(code, 0)

def part1(data: ParsedData) -> int:
    return solver(data, 1)

def solver(data: ParsedData, part: int) -> int:
    final_val = 0
    for code in data.codes:
        moves_len = find_button_sequence_length(code, robots=2 if part == 1 else 25)
        code_num = ''.join([c for c in code.lstrip('0') if c.isnumeric()])
        res = moves_len * int(code_num)
        final_val += res
    return final_val


def part2(data: ParsedData) -> int:
    return solver(data, 2)

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input = """
029A
980A
179A
456A
379A
"""
    all_pass = True
    if part == 1:
        all_pass = all_pass and verify_result(part1(parse_input(test_input)), 126384, 1)

    return all_pass

if __name__ == "__main__":
    run_tests(21)
    run_day(21, part1=True, part2=True)
