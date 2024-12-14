from typing import List, Tuple
from collections import defaultdict

from common import verify_result, run_day, run_tests
from functools import cmp_to_key
from PIL import Image, ImageDraw, ImageFont

frames = []  # global or passed around, will collect all frames

# Class
class ParsedData:
    __slots__ = ["grid", "width", "height"]

    def __init__(self):
        self.grid: List[List[int]] = []
        self.width: int = 0
        self.height: int = 0

def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    lines = [l.strip('\r') for l in data.split('\n') if l.strip('\r')]
    for y, line in enumerate(lines):
        row = []
        for x, ch in enumerate(line):
            val = int(ch)
            row.append(val)
        result.grid.append(row)
    result.height = len(result.grid)
    result.width = len(result.grid[0])
    return result

def part1(data: ParsedData) -> int:
    return solver(data, 1)

Point = Tuple[int, int]

class TrailHead:
    __slots__ = ['pos', 'paths']
    def __init__(self, position: Point):
        self.pos = position
        self.paths = List[List[Point]]()

def gridWalk(data: ParsedData, pt: Point, path: List[Point]) -> List[List[Point]]:
    prev = data.grid[path[-1][1]][path[-1][0]] if len(path) > 0 else 0

    if prev == 9:
        return [path]

    result = []
    dirs = [(0, -1), (-1, 0), (0, 1), (1, 0)]

    for dir in dirs:
        x, y = pt
        x += dir[0]
        y += dir[1]
        if x < 0 or x >= data.width or y < 0 or y >= data.height:
            continue
        new = data.grid[y][x]
        if prev + 1 != new:
            continue
        new_path = path.copy()
        new_path.append((x, y))
        paths = gridWalk(data, (x, y), new_path)
        result.extend(paths)

    return result


def draw_grid_with_paths(data: ParsedData, paths: List[List[Point]], max_height: int) -> None:
    from PIL import Image, ImageDraw, ImageFont

    cell_size = 20
    img_width = data.width * cell_size
    img_height = data.height * cell_size
    img = Image.new("RGB", (img_width, img_height), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    path_points = set(pt for p in paths for pt in p)
    start_points = set(p[0] for p in paths if p)

    non_path_bg = (220, 220, 220)
    path_bg = (180, 180, 180)
    start_color = (0, 0, 255)
    nine_color = (255, 0, 0)
    path_color = (0, 128, 0)
    default_color = (0, 0, 0)

    # Softer blue for zero from path
    zero_bg = (50, 100, 255)
    zero_text = (200, 200, 200)

    for y in range(data.height):
        for x in range(data.width):
            val = data.grid[y][x]
            x0 = x * cell_size
            y0 = y * cell_size

            if (x, y) in path_points:
                if val == 0:
                    draw.rectangle([x0, y0, x0+cell_size, y0+cell_size], fill=zero_bg)
                    draw.text((x0+5, y0+5), str(val), font=font, fill=zero_text)
                else:
                    draw.rectangle([x0, y0, x0+cell_size, y0+cell_size], fill=path_bg)
                    if val > max_height:
                        draw.text((x0+5, y0+5), str(val), font=font, fill=default_color)
                    else:
                        if (x, y) in start_points:
                            draw.text((x0+5, y0+5), str(val), font=font, fill=start_color)
                        elif val == 9:
                            draw.text((x0+5, y0+5), str(val), font=font, fill=nine_color)
                        else:
                            draw.text((x0+5, y0+5), str(val), font=font, fill=path_color)
            else:
                draw.rectangle([x0, y0, x0+cell_size, y0+cell_size], fill=non_path_bg)
                draw.text((x0+5, y0+5), str(val), font=font, fill=default_color)

    frames.append(img)



def solver(data: ParsedData, part: int) -> int:
    total = 0

    ENABLE_SAVE_2_GIF = True

    for y in range(data.height):
        for x in range(data.width):
            if data.grid[y][x] != 0:
                continue
            paths = gridWalk(data, (x, y), [(x, y)])
            if part == 1:
                dest_9_positions: set[Point] = set()
                for path in paths:
                    if len(path) == 10:
                        dest_9_positions.add(path[-1])
                total += len(dest_9_positions)
            else:
                total += len(paths)

            if ENABLE_SAVE_2_GIF:
                for h in range(0, 10):
                    draw_grid_with_paths(data, paths, h)

    if ENABLE_SAVE_2_GIF:
        if len(frames) > 0:
            frames[0].save('day10_animation.gif', save_all=True, append_images=frames[1:], duration=200, loop=0, optimize=True)

    return total


def part2(data: ParsedData) -> int:
    return solver(data, 2)

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> None:
    test_input = """
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    # Test part 1
    if (part == 1):
        all_pass = all_pass and verify_result(part1(parsed_data), 36, 1)

    # Test part 2
    if (part == 2):
        all_pass = all_pass and verify_result(part2(parsed_data), 81, 2)

    return all_pass

if __name__ == "__main__":
    #run_tests(10)
    run_day(10, part1=True, part2=False)
