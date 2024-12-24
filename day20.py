from collections import deque
from typing import List, Tuple, Set, Dict, Optional

from common import run_day, verify_result, run_tests

class ParsedData:
    __slots__ = ["grid", "start", "end", "rows", "cols"]

    def __init__(self):
        self.grid: List[List[str]] = []
        self.start: Tuple[int, int] = (-1, -1)
        self.end: Tuple[int, int] = (-1, -1)
        self.rows: int = 0
        self.cols: int = 0

def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    lines = data.strip().split('\n')
    result.grid = [list(line) for line in lines]
    result.rows = len(result.grid)
    result.cols = len(result.grid[0]) if result.rows > 0 else 0
    for r in range(result.rows):
        for c in range(result.cols):
            if result.grid[r][c] == 'S':
                result.start = (r, c)
            elif result.grid[r][c] == 'E':
                result.end = (r, c)
    return result


Point2 = Tuple[int, int]
def bfs_with_path(grid: List[List[str]], start: Point2, end: Point2) -> Tuple[List[List[int]], List[Point2]]:
    """
    Perform BFS to assign distances from the start to all reachable cells and reconstruct the shortest path to the end.

    Parameters:
    - grid (List[List[str]]): The racetrack map.
    - start (Point2): Starting position (row, column).
    - end (Point2): Ending position (row, column).

    Returns:
    - Tuple containing:
        - distances (List[List[int]]): 2D grid of distances from the start. Unreachable cells have distance -1.
        - path (List[Point2]): The shortest path from start to end as a list of (row, column) tuples. Empty if no path exists.
    """
    rows, cols = len(grid), len(grid[0])

    # Initialize the distance grid with -1 (unreachable)
    distances = [[-1 for _ in range(cols)] for _ in range(rows)]

    # Initialize the predecessor grid with None
    predecessors: List[List[Optional[Point2]]] = [[None for _ in range(cols)] for _ in range(rows)]

    # Initialize the BFS queue
    queue = deque()
    queue.append(start)
    distances[start[0]][start[1]] = 0  # Distance to start is 0

    # Define movement directions: Up, Down, Left, Right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        current = queue.popleft()
        r, c = current
        current_distance = distances[r][c]

        # Early termination if end is reached
        if current == end:
            break

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                # Check if the cell is not a wall and not visited
                if grid[nr][nc] != '#' and distances[nr][nc] == -1:
                    distances[nr][nc] = current_distance + 1
                    predecessors[nr][nc] = (r, c)
                    queue.append((nr, nc))

    # Reconstruct the path from end to start
    path: List[Point2] = []
    if distances[end[0]][end[1]] != -1:
        current = end
        while current != start:
            path.append(current)
            current = predecessors[current[0]][current[1]]
            if current is None:
                # This should not happen as we have a valid path
                break
        path.append(start)
        path.reverse()  # Path from start to end

    return distances, path

Shortcuts = Set[Tuple[int, int, int, int, int]] # (r, c, nr, nc, savings) - shortcut_start, shortcut_end, savings
def find_shortcuts(data: ParsedData, minimum_savings: int, max_delta: int) -> Shortcuts:
    """
    Find the number of unique cheats (shortcuts) that save at least 'minimum_savings' picoseconds.
    Each cheat is uniquely identified by its (cheat_start, cheat_end).
    This function considers shortcuts within a 'max_delta' Manhattan distance.
    """
    distances, path = bfs_with_path(data.grid, data.start, data.end)
    rows, cols = data.rows, data.cols

    potential_shortcuts = []

    # Iterate all path cells (actually its as fast as iterate all rc in grid)
    for (r,c) in path:
        cell_dist_from_start = distances[r][c]
        if cell_dist_from_start == -1:
            continue # Ignore not reachable cells (also walls)

        # (r,c) is a reachable from start cell. Check all cells within a Manhattan distance of 'max_delta'.
        for delta_row in range(-max_delta, max_delta+1):
            for delta_col in range(-max_delta, max_delta+1):
                if delta_row == 0 and delta_col == 0:
                    continue # Skip the same cell

                #shortcut_dist = abs(delta_row) + abs(delta_col) # Actually a manhattan distance
                shortcut_dist = (delta_row if delta_row >= 0 else -delta_row) + (
                    delta_col if delta_col >= 0 else -delta_col)
                if shortcut_dist > max_delta:
                    continue # Skip cells outside the Manhattan distance

                nr, nc = r + delta_row, c + delta_col
                if 0 <= nr < rows and 0 <= nc < cols:
                    nrnc_cell_distance = distances[nr][nc]
                    if nrnc_cell_distance == -1:
                        continue  # Unreachable (wall)

                    # Calculate the savings by taking the shortcut. So if we would jump to (nr, nc) from (r, c),
                    # how much time would we save?
                    savings = nrnc_cell_distance - cell_dist_from_start - shortcut_dist
                    # savings can be negative if the (nr,nc) cell is on path that was already visited.
                    if savings >= minimum_savings:
                        potential_shortcuts.append((r, c, nr, nc, savings))

    unique_shortcuts = set(potential_shortcuts)
    return unique_shortcuts


def printMap(grid: List[List[str]],
            path: List[Tuple[int, int]] = None,
            cheat_steps: Dict[int, str] = None) -> None:
    grid_copy = [row.copy() for row in grid]
    if path:
        for index, (r, c) in enumerate(path):
            if grid_copy[r][c] in ('S', 'E'):
                continue
            if cheat_steps and index in cheat_steps:
                grid_copy[r][c] = cheat_steps[index]
            else:
                grid_copy[r][c] = '.'
    for row in grid_copy:
        print(''.join(row))


def part1(data: ParsedData) -> int:
    # Find the number of unique cheats that save at least 100 picoseconds withing a manhattan distance of 2.
    best_shortcuts = find_shortcuts(data, minimum_savings=100, max_delta=2)
    return len(best_shortcuts)


def part2(data: ParsedData) -> int:
    # Find the number of unique cheats that save at least 100 picoseconds,
    # considering shortcuts within a manhattan distance of 20.
    best_shortcuts = find_shortcuts(data, minimum_savings=100, max_delta=20)
    return len(best_shortcuts)


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input = """
###############
#...#...#.....#
#.#.#.#.#.###.#
#S#...#.#.#...#
#######.#.#.###
#######.#.#...#
#######.#.###.#
###..E#...#...#
###.#######.###
#...###...#...#
#.#####.#.###.#
#.#...#.#.#...#
#.#.#.#.#.#.###
#...#...#...###
###############
    """
    parsed_data = parse_input(test_input)
    all_passed = True
    if part == 1:
        best_shortcuts = find_shortcuts(parsed_data, minimum_savings=0, max_delta=2)

        #convert best_sortcuts to a dictionary
        cheat_dict = {}
        for cheat in best_shortcuts:
            cheat_dict[cheat[4]] = cheat_dict.get(cheat[4], []) + [cheat]

        res = ""
        for time in sorted(cheat_dict.keys()):
            count = len(cheat_dict[time])
            if time == 0:
                continue
            s = f" - There {"is" if count == 1 else "are"} {"one" if count == 1 else count} {"cheat" if count == 1 else "cheats"} that {"saves" if count == 1 else "save"} {time} picoseconds."
            #print(s)
            res += "\n" + s
        expected = """
 - There are 14 cheats that save 2 picoseconds.
 - There are 14 cheats that save 4 picoseconds.
 - There are 2 cheats that save 6 picoseconds.
 - There are 4 cheats that save 8 picoseconds.
 - There are 2 cheats that save 10 picoseconds.
 - There are 3 cheats that save 12 picoseconds.
 - There is one cheat that saves 20 picoseconds.
 - There is one cheat that saves 36 picoseconds.
 - There is one cheat that saves 38 picoseconds.
 - There is one cheat that saves 40 picoseconds.
 - There is one cheat that saves 64 picoseconds."""
        #diff_result = git_like_diff(res, expected, fromfile='Original', tofile='Modified')
        #print(diff_result)
        all_passed = all_passed and verify_result(res, expected, 1)
    return all_passed


if __name__ == "__main__":
    run_tests(20)
    run_day(20, part1=True, part2=True)
