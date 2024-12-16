from typing import List, Tuple
from common import run_tests, run_day, verify_result


class ParsedData:
    __slots__ = ["robots"]

    def __init__(self):
        # x: The x-coordinate of the robot's initial position.
        # y: The y-coordinate of the robot's initial position.
        # dx: The x-component of the robot's velocity.
        # dy: The y-component of the robot's velocity.
        self.robots: List[Tuple[int, int, int, int]] = [] # (x, y, dx, dy)

def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    lines = data.strip().split("\n")
    for line in lines:
        if not line.strip():
            continue
        # Line format: p=x,y v=dx,dy
        parts = line.split()
        p_part = parts[0][2:]  # Remove 'p='
        v_part = parts[1][2:]  # Remove 'v='
        x, y = map(int, p_part.split(','))
        dx, dy = map(int, v_part.split(','))
        result.robots.append((x, y, dx, dy))
    return result

def bounding_box(robots: List[Tuple[int, int, int, int]], t: int, width, height):
    xs = [(x + dx * t)%width for (x, y, dx, dy) in robots]
    ys = [(y + dy * t)%height for (x, y, dx, dy) in robots]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    area = (max_x - min_x) * (max_y - min_y)
    return area, min_x, max_x, min_y, max_y

def print_pattern(robots: List[Tuple[int, int, int, int]], t: int, width, height) -> None:
    _, min_x, max_x, min_y, max_y = bounding_box(robots, t, width, height)
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    grid = [['.' for _ in range(width)] for _ in range(height)]

    for (x, y, dx, dy) in robots:
        X = (x + dx * t)%width
        Y = (y + dy * t)%height
        # Ensure that the coordinates are within the grid bounds
        if min_x <= X <= max_x and min_y <= Y <= max_y:
            grid[Y - min_y][X - min_x] = '#'

    for row in grid:
        print("".join(row))

def find_christmas_tree_time(robots: List[Tuple[int, int, int, int]], width: int, height: int) -> int:
    safety_cutoff = 200000000

    map_dict = {}
    for t in range(1, safety_cutoff, 1):
        same_position_count = 0
        for (x, y, dx, dy) in robots:
            final_x = (x + t * dx) % width
            final_y = (y + t * dy) % height
            if (final_x, final_y) in map_dict and map_dict[(final_x, final_y)] == t:
                same_position_count += 1
                break
            map_dict[(final_x, final_y)] = t
        if same_position_count == 0:

            # Gives correct result, but visually does not look like a Christmas tree at all
            #print_pattern(robots, t, width, height)
            #for t2 in range(t, t+30):
            #    print(f"Time = {t2}")
            #    print_pattern(robots, t2, width, height)

            return t
    return 0


def solver(data: ParsedData, part: int, width: int, height: 103) -> int:

    if part == 1:
        # Part 1: Calculate the safety factor after 100 seconds
        center_x = width // 2  # 50
        center_y = height // 2  # 51
        time = 100

        Q1 = Q2 = Q3 = Q4 = 0

        for (x, y, dx, dy) in data.robots:
            final_x = (x + time * dx) % width
            final_y = (y + time * dy) % height

            if final_x == center_x or final_y == center_y:
                continue  # Robots exactly on the center lines are not counted

            if final_x > center_x and final_y < center_y:
                Q1 += 1
            elif final_x < center_x and final_y < center_y:
                Q2 += 1
            elif final_x < center_x and final_y > center_y:
                Q3 += 1
            elif final_x > center_x and final_y > center_y:
                Q4 += 1

        return Q1 * Q2 * Q3 * Q4
    else:
        # Part 2: Find the time when the robots form the Easter egg pattern
        best_t = find_christmas_tree_time(data.robots, width, height)
        return best_t


def part1(data: ParsedData, width: int, height: int) -> int:
    return solver(data, 1, width, height)


def part2(data: ParsedData, width: int, height: int) -> int:
    return solver(data, 2, width, height)


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data, width=101, height=103) if part == 1 else part2(parsed_data, width=101, height=103)


def test(part) -> bool:
    test_input = """
p=0,4 v=3,-3
p=6,3 v=-1,-3
p=10,3 v=-1,2
p=2,0 v=2,-1
p=0,0 v=1,3
p=3,0 v=-2,-2
p=7,6 v=-1,-3
p=3,0 v=-1,-2
p=9,3 v=2,3
p=7,3 v=-1,2
p=2,4 v=2,-3
p=9,5 v=-3,-3
""".strip()

    if part == 1:
        return verify_result(part1(parse_input(test_input), width=11, height=7), 12, 1)
    return True

if __name__ == "__main__":
    run_tests(14)
    run_day(14, part1=True, part2=True)
