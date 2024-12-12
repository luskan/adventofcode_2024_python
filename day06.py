from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor

from common import run_day

GRID_WALL = 2
GRID_EMPTY = 1
GRID_GUARD = 0

char_map = {
    '#': GRID_WALL,
    '.': GRID_EMPTY,
    '^': GRID_EMPTY
}

class ParsedData:
    __slots__ = ['grid', 'start_point']
    def __init__(self):
        self.grid: List[List[int]] = []
        self.start_point: Tuple[int, int] = (0, 0)

def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    lines = [l.strip('\r') for l in data.split('\n') if l.strip('\r')]
    for y, line in enumerate(lines):
        row = []
        caret_ind = -1
        for x, ch in enumerate(line):
            val = char_map.get(ch, GRID_GUARD)
            if ch == '^':
                caret_ind = x
            row.append(val)
        result.grid.append(row)
        if caret_ind != -1:
            result.start_point = (caret_ind, y)
    return result

class SimulationResults:
    __slots__ = ['visited_set', 'end_point', 'loop']
    def __init__(self):
        self.visited_set = set()
        self.end_point = (-1, -1)
        self.loop = False

def direction_to_index(dx: int, dy: int) -> int:
    # map dx,dy to a direction index
    # (0,-1) up=0, (-1,0) left=1, (0,1) down=2, (1,0) right=3
    if dx == 0 and dy == -1:
        return 0
    elif dx == -1 and dy == 0:
        return 1
    elif dx == 0 and dy == 1:
        return 2
    elif dx == 1 and dy == 0:
        return 3

def simulateGuardWalking(data: ParsedData, max_width: int, max_height: int, extra_obstacle: Tuple[int, int],
                         collect_visited: bool, results: SimulationResults, turn_points: List[int], iteration: int):
    x, y = data.start_point
    dx, dy = 0, -1
    grid = data.grid
    obstacle = extra_obstacle

    vs = results.visited_set if collect_visited else None
    if vs is not None:
        vs.add((x, y))

    while True:
        x_new = x + dx
        y_new = y + dy

        # out of bounds?
        if x_new < 0 or x_new >= max_width or y_new < 0 or y_new >= max_height:
            results.end_point = (x_new, y_new)
            return

        cell_val = grid[y_new][x_new]
        if cell_val == GRID_WALL or (x_new, y_new) == obstacle:
            # we turn around here
            if turn_points is not None:
                dir_idx = direction_to_index(dx, dy)
                turn_id_idx = (y * max_width + x) * 4 + dir_idx
                if turn_points[turn_id_idx] == iteration:
                    results.loop = True
                    return
                turn_points[turn_id_idx] = iteration

            # rotate direction: (dx, dy) -> (-dy, dx)
            dx, dy = -dy, dx
        else:
            x, y = x_new, y_new
            if vs is not None:
                vs.add((x, y))

def part1(data: ParsedData) -> int:
    results = SimulationResults()
    h, w = len(data.grid), len(data.grid[0])
    simulateGuardWalking(data, w, h, (-1, -1), True, results, None, -1)
    return len(results.visited_set)

def process_range_of_points(start: int, end: int, data: ParsedData, max_width: int, max_height: int, visited_list: List[Tuple[int,int]]) -> int:
    # Initialize array which will allow to check if we have a loop.
    #
    # Turn points are stored in an array of size max_width * max_height * 4
    # each point has 4 directions, so we store the iteration number for each point and direction
    # to check if we have a loop. The index is calculated as (y * max_width + x) * 4 + direction_index
    # where direction_index is 0 for up, 1 for left, 2 for down, 3 for right.
    #
    # To avoid clearing the array for each iteration, we store the iteration number for each point and direction
    # if the iteration number is the same as the current iteration, we have a loop. If the iteration number is less
    # than the current iteration, then it means no turn at this place was found in current iteration.
    #
    # Previously I used set and switched to this solution to check if it makes it any faster, but if it did then
    # in a small amount (~5%).
    turn_points_size = max_width * max_height * 4
    turn_points = [-1] * turn_points_size

    tested_obstacles = set()
    local_valid_moves = 0

    results = SimulationResults()
    for i in range(start, end):
        point = visited_list[i]
        sp = data.start_point
        #skip the start point and already tested obstacles
        if point == sp or point in tested_obstacles:
            continue
        tested_obstacles.add(point)

        results.visited_set.clear()
        results.loop = False
        simulateGuardWalking(data, max_width, max_height, point, False, results, turn_points, i)
        if results.loop:
            local_valid_moves += 1

    return local_valid_moves

def process_range_wrapper(args):
    return process_range_of_points(*args)

def part2(data: ParsedData, num_processes: int = 4) -> int:
    #initialize the simulation results and get the grid dimensions
    initial_results = SimulationResults()
    h, w = len(data.grid), len(data.grid[0])

    #initial simulation to get the list of visited points which are candidates for obstacles
    simulateGuardWalking(data, w, h, (-1, -1), True, initial_results, None, -1)

    #list of visited points excluding the start point
    sp = data.start_point
    visited_list = [v for v in initial_results.visited_set if v != sp]
    num_points = len(visited_list)

    # step size for dividing the work among processes
    step = (num_points + num_processes - 1) // num_processes

    #calc ranges for each process to work on
    ranges = [(r, min(r+step, num_points), data, w, h, visited_list) for r in range(0, num_points, step)]

    #parallelize the work
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        results = executor.map(process_range_wrapper, ranges)

    #sum the results from all processes
    return sum(results)

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
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
    return (part1(parsed_data) == 41) if part == 1 else (part2(parsed_data) == 6)

if __name__ == "__main__":
    run_day(6, part1=False, part2=True)
