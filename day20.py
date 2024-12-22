import heapq
from typing import List, Tuple, Set, Dict, Optional
from collections import deque, defaultdict

from common import run_tests, run_day, git_like_diff, verify_result


# Class to store parsed data
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



def printMap(grid: List[List[str]],
             path: List[Tuple[int, int]] = None,
             cheat_steps: List[Tuple[int, int]] = None) -> None:
    """
    Prints the map with the path and cheat steps overlaid.

    Parameters:
    - grid (List[List[str]]): The racetrack map.
    - path (List[Tuple[int, int]], optional): The sequence of positions from start to end.
    - cheat_steps (Dict[int, str], optional): A mapping from path indices to cheat labels ('1' or '2').

    Returns:
    - None
    """
    # Create a deep copy of the grid to overlay the path and cheats
    grid_copy = [row.copy() for row in grid]

    if path:
        for index, (r, c) in enumerate(path):
            # Skip the start and end positions to preserve 'S' and 'E'
            if grid_copy[r][c] in ('S', 'E'):
                continue

            # Check if the current path step is part of a cheat
            if cheat_steps and (r, c) in cheat_steps:
                grid_copy[r][c] = str(cheat_steps.index((r, c))+1) # Mark with '1' or '2'
            else:
                grid_copy[r][c] = '\033[91mO\033[0m'  # Mark the path

    # Print the modified grid
    for row in grid_copy:
        print(''.join(row))


def a_star_min_time(grid: List[List[str]],
                    start: Tuple[int, int],
                    end: Tuple[int, int],
                    cheat_start_time: int,
                    valid_cheat_positions: List[Tuple[int, int]],
                    return_path: bool = False) -> Tuple[int, List[Tuple[int, int]]]:
    """
    Perform A* search to find the shortest path from start to end considering cheat time.
    Returns a tuple containing:
        - The minimal time (number of moves) to reach the end.
        - The path as a list of (row, column) tuples from start to end.
    """
    rows, cols = len(grid), len(grid[0])

    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Priority queue elements: (f_cost, g_cost, (r, c))
    open_set = []
    start_h = heuristic(start, end)
    heapq.heappush(open_set, (start_h, 0, start))

    # Maps (r, c) to its predecessor
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}

    # Maps (r, c) to the lowest g_cost found so far
    g_cost: Dict[Tuple[int, int], int] = {start: 0}

    # Define movement directions: Up, Down, Left, Right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while open_set:
        current_f, current_g, current = heapq.heappop(open_set)
        r, c = current

        # Check if we've reached the end
        if current == end:
            # Reconstruct the path from end to start
            path = []
            if return_path:
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
            return current_g, path

        # Determine the current time based on g_cost
        time = current_g

        is_cheat = cheat_start_time != -1 and cheat_start_time <= time <= cheat_start_time + 1

        # If not in cheat time and current cell is a wall, skip
        if not is_cheat and grid[r][c] == '#':
            continue

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)

            # Check boundaries
            if 0 <= nr < rows and 0 <= nc < cols:
                # Determine if the neighbor cell can be traversed

                if is_cheat and cheat_start_time == 20 and neighbor == (9,8) and (8,10) in valid_cheat_positions:
                    pass

                if (is_cheat and neighbor in valid_cheat_positions or grid[nr][nc] != '#') and neighbor not in came_from:
                    tentative_g = current_g + 1  # Assuming uniform cost
                    if neighbor not in g_cost or tentative_g < g_cost[neighbor]:
                        g_cost[neighbor] = tentative_g
                        f_cost = tentative_g + heuristic(neighbor, end)
                        heapq.heappush(open_set, (f_cost, tentative_g, neighbor))
                        if return_path:
                            came_from[neighbor] = current

    # If the end is not reachable
    return -1, []


Point2 = Tuple[int, int]
CheatsDict = Dict[int, List[Tuple[Point2, Point2]]]
def find_all_valid_cheats(data: ParsedData) -> CheatsDict:
    """
    Find the number of unique cheats that save at least 100 ps.
    Each cheat is uniquely identified by its (cheat_start, cheat_end).
    """
    cheats: CheatsDict = {}

    no_cheat_min_time, no_cheat_path = a_star_min_time(data.grid, data.start, data.end, -1, [], return_path=True)

    for cheat_time in range(len(no_cheat_path) - 1):
        if cheat_time % 100 == 0:
            print(f"Processing cheat time {cheat_time}...")
        no_cheat_pos = no_cheat_path[cheat_time]

        # Collect, position in grid around no_cheat_pos, which are not on no_cheat_path
        valid_cheat_positions: List[List[Tuple[int,int]]] = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = no_cheat_pos[0] + dr, no_cheat_pos[1] + dc
            if 0 <= nr < data.rows and 0 <= nc < data.cols and (nr, nc) not in no_cheat_path:
                if data.grid[nr][nc] == '#':
                    valid_cheat_positions.append([(nr, nc)])
                # Now for (nr,nc) Collect, position in grid around no_cheat_pos, which are not on no_cheat_path
                """
                for dr2, dc2 in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr2, nc2 = nr + dr2, nc + dc2
                    if 0 <= nr2 < data.rows and 0 <= nc2 < data.cols and (nr2, nc2) not in no_cheat_path:
                        pos = [(nr, nc),(nr2, nc2)]
                        if pos not in valid_cheat_positions:
                            valid_cheat_positions.append(pos)
                """

        for cheat_points in valid_cheat_positions:
            t1, path = a_star_min_time(grid=data.grid, start=data.start, end=data.end, cheat_start_time=cheat_time, valid_cheat_positions=cheat_points, return_path=False)

            """
            if cheat_time == 20:
                print(f"\n{cheat_time} - t1={t1} - save={no_cheat_min_time-t1} - cheat_points={cheat_points} - saving={no_cheat_min_time-t1}")
                cheat_start = path[cheat_time]
                cheat_end = path[cheat_time + 1]
                printMap(grid=data.grid, path=path, cheat_steps=[cheat_start, cheat_end])
                pass
            """

            if t1 > -1:
                cheat_start = (-1,-1) # path[cheat_time]
                cheat_end = (-1,-1) # path[cheat_time+1]
                #print(f"\n{cheat_time}")
                #printMap(grid=data.grid, path=path, cheat_steps=[cheat_start, cheat_end])
                #print()
                saving = no_cheat_min_time - t1
                #if saving >= 100:
                if saving not in cheats:
                    cheats[saving] = []
                cheats[saving].append((cheat_start, cheat_end))

    return cheats


def part1(data: ParsedData) -> CheatsDict:
    # Find minimal time without cheating
    cheatsDict = find_all_valid_cheats(data)
    return cheatsDict


def part2(data: ParsedData) -> CheatsDict:
    return {}

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    cheatsDict = part1(parsed_data)
    total = 0
    for key, value in cheatsDict.items():
        if key >= 100:
            total += len(value)
    return total

def test(part) -> bool:
    # Placeholder for running the solution
    # Replace this with actual input reading if necessary
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
    if part == 1:
        cheats = part1(parsed_data)

        print()
        res = ""
        for time in sorted(cheats.keys()):
            count = len(cheats[time])
            if time == 0:
                continue
            s = f" - There {"is" if count == 1 else "are"} {"one" if count == 1 else count} {"cheat" if count == 1 else "cheats"} that {"saves" if count == 1 else "save"} {time} picoseconds."
            print(s)
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
        diff_result = git_like_diff(res, expected, fromfile='Original', tofile='Modified')
        print(diff_result)
        verify_result(res, expected, 1)

        #expected1 = 84  # As per the problem statement
        #verify_result(result1, expected1, 1)
    #if part == 2:
    #    result2 = part2(parsed_data)
    #    expected2 = 0  # As per the sample, no cheat saves >=100 ps
    #    verify_result(result2, expected2, 2)


# Run the test
if __name__ == "__main__":
    #run_tests(20)
    run_day(20, part1=True, part2=False) # 9448 is too high
