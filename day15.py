from typing import List, Tuple

from common import run_tests, run_day, verify_result

class ParsedData:
    __slots__ = ["map_lines", "moves_str"]

    def __init__(self):
        self.map_lines = []
        self.moves_str = []

def parse_input(data: str) -> 'ParsedData':
    result: ParsedData = ParsedData()

    # Read lines and split map from moves
    all_lines = data.split('\n')
    all_lines = [l.rstrip() for l in all_lines]

    blank_line_index = None
    for i, line in enumerate(all_lines):
        if line.strip() == "":
            blank_line_index = i
            break

    if blank_line_index is None:
        assert False, "Invalid input"
    else:
        result.map_lines = all_lines[:blank_line_index]
        moves_lines = all_lines[blank_line_index+1:]
        result.moves_str = "".join(moves_lines)
        result.moves_str = result.moves_str.replace(" ", "")

    return result

def part1(data: ParsedData) -> int:
    return solver(data, 1)

def part2(data: ParsedData) -> int:
    return solver(data, 2)

def solver(data: ParsedData, part: int) -> int:
    map_lines = data.map_lines
    moves_str = data.moves_str

    # If part 2, scale the map
    if part == 2:
        map_lines = scale_map(map_lines)

    warehouse = [list(row) for row in map_lines]
    rows = len(warehouse)
    cols = len(warehouse[0]) if rows > 0 else 0

    # Find robot position '@'
    robot_r, robot_c = None, None
    for r in range(rows):
        for c in range(cols):
            if warehouse[r][c] == '@':
                robot_r, robot_c = r, c
                break
        if robot_r is not None:
            break

    deltas = {
        '^': (-1, 0),
        'v': (1, 0),
        '<': (0, -1),
        '>': (0, 1)
    }

    print("")
    iter = 0
    AllowPrint = False

    # Run simulation
    for move in moves_str:
        dr, dc = deltas[move]
        new_r = robot_r + dr
        new_c = robot_c + dc

        if not (0 <= new_r < rows and 0 <= new_c < cols):
            # Out of range move
            continue

        target_cell = warehouse[new_r][new_c]

        if part == 2 and AllowPrint:
            # print map
            if iter == 5:
                pass
            print(f"{iter}# Move: {move}:")
            for row in warehouse:
                print("".join(row))
            print("")
            iter += 1

        if target_cell == '#':
            # Wall, no move
            continue
        elif target_cell == '.':
            warehouse[robot_r][robot_c] = '.'  # old cell becomes floor
            warehouse[new_r][new_c] = '@'
            robot_r, robot_c = new_r, new_c
        else:
            # Encounter box(es)
            can_push = False
            if part == 1:
                # Part 1 pushing logic
                if target_cell == 'O':
                    can_push = push_boxes_part1(warehouse, robot_r, robot_c, dr, dc)
            else:
                # Part 2 pushing logic
                if target_cell == '[' or target_cell == ']':
                    can_push = push_boxes_part2(warehouse, robot_r, robot_c, dr, dc)
            if can_push:
                    warehouse[robot_r][robot_c] = '.'  # Clear '@'
                    warehouse[robot_r + dr][robot_c + dc] = '@'
                    robot_r += dr
                    robot_c += dc

    if part == 2 and AllowPrint:
        # print map
        if iter == 5:
            pass
        print(f"{iter}# Move: {move}:")
        for row in warehouse:
            print("".join(row))
        print("")
        iter += 1

    return sum_boxes(warehouse, part)

def push_boxes_part1(warehouse: List[List[str]], robot_r: int, robot_c: int, dr: int, dc: int) -> bool:
    # Push logic for part 1 (single cell boxes 'O')
    rows = len(warehouse)
    cols = len(warehouse[0]) if rows > 0 else 0

    # Gather consecutive boxes
    check_r = robot_r + dr
    check_c = robot_c + dc
    boxes = []
    while 0 <= check_r < rows and 0 <= check_c < cols:
        if warehouse[check_r][check_c] == 'O':
            boxes.append((check_r, check_c))
            check_r += dr
            check_c += dc
        else:
            break

    if not (0 <= check_r < rows and 0 <= check_c < cols):
        # Out of range, can't push
        return False
    if warehouse[check_r][check_c] != '.':
        # Not empty, can't push
        return False

    # We can push
    # Clear robot old cell
    warehouse[robot_r][robot_c] = '.'
    # Move boxes from last to first
    for br, bc in reversed(boxes):
        warehouse[br + dr][bc + dc] = 'O'
        warehouse[br][bc] = '.'
    # Move robot into first box's old position
    warehouse[robot_r + dr][robot_c + dc] = '@'
    return True

def push_boxes_part2(warehouse: List[List[str]], robot_r: int, robot_c: int, dr: int, dc: int) -> bool:
    # Push logic for part 2 (two-cell boxes '[]')

    # Recursively check if a a box can be moved at given point. Robot is represented by one point
    # while a box-s move is represented by two points. This aproach could also be used in part 1.

    def try_move_boxes(move_points: List[Tuple[int,int]]) -> Tuple[bool, List[Tuple[int,int]]]:

        # find all boxes that are colliding with the robot, return a tuple with bool as first value
        # indicating if a move is possible - ie. if a wall was encountered at some resurse level. If true
        # is returned then all the boxes which were found to be moved, along the resurce descent, are returned in second
        # tuple element

        boxes_to_be_moved = []
        # Iterate all the move points
        for mp_r, mp_c in move_points:
            mp_boxes_to_be_moved = []

            # If wall, then return down the recursive call tree that this move is blocked.
            if warehouse[mp_r][mp_c] == '#':
                return False, []
            if warehouse[mp_r][mp_c] == '.':
                continue

            # Move encounters a box, we will resursively check if moving it is possible and which (if any) new box
            # moves it creates.
            if warehouse[mp_r][mp_c] == '[' or warehouse[mp_r][mp_c] == ']':

                #ab_r ab_c repesent one box position always by its left side.
                ab_r, ab_c = mp_r, mp_c + (-1 if warehouse[mp_r][mp_c] == ']' else 0)

                if dc != 0:
                    # For horizontal movement single point is generated. It must also be aligned to direction of move.
                    new_move_points = [(ab_r, ab_c + dc + (0 if dc < 0 else 1))]
                else:
                    # For vertical we have two move points one is for [ and the other for ]
                    new_move_points = [(ab_r + dr, ab_c), (ab_r + dr, ab_c + 1)]
                can_move, all_moved_boxes = try_move_boxes(new_move_points)
                if not can_move:
                    # If move not allowed (a # was encountered at some resursive descent), then abort move
                    # until the very top of the calls.
                    return False, []

                # If move allowed, then store all the boxes that can be moved.
                mp_boxes_to_be_moved.extend(all_moved_boxes)
                mp_boxes_to_be_moved.append((ab_r, ab_c))
            boxes_to_be_moved.extend(mp_boxes_to_be_moved)
        return True, boxes_to_be_moved

    # Check which boxes can be moved, and if the move is actually possible.
    can_move, boxes_to_move = try_move_boxes([(robot_r + dr, robot_c + dc)])
    if not can_move:
        return False

    # Clear map
    warehouse[robot_r][robot_c] = '.'
    for ab_r, ab_c in boxes_to_move:
        warehouse[ab_r][ab_c] = '.'
        warehouse[ab_r][ab_c+1] = '.'

    # Set new positions
    for ab_r, ab_c in boxes_to_move:
        warehouse[ab_r + dr][ab_c+dc] = '['
        warehouse[ab_r + dr][ab_c+dc+1] = ']'
    warehouse[robot_r + dr][robot_c + dc] = '@'

    return True

def scale_map(map_lines: List[str]) -> List[str]:
    # Scale map horizontally:
    # '#' -> '##'
    # 'O' -> '[]'
    # '.' -> '..'
    # '@' -> '@.'
    # '[]' boxes are handled as separate entities
    scaled = []
    for line in map_lines:
        new_line = []
        for ch in line:
            if ch == '#':
                new_line.append('##')
            elif ch == 'O':
                new_line.append('[]')
            elif ch == '.':
                new_line.append('..')
            elif ch == '@':
                new_line.append('@.')
            else:
                # If something unexpected, treat as floor
                new_line.append('..')
        scaled.append("".join(new_line))
    return scaled

def sum_boxes(warehouse: List[List[str]], part: int) -> int:
    rows = len(warehouse)
    cols = len(warehouse[0]) if rows > 0 else 0
    total = 0
    if part == 1:
        # Sum 'O' positions
        for r in range(rows):
            for c in range(cols):
                if warehouse[r][c] == 'O':
                    total += 100 * r + c
    else:
        # Part 2: Sum positions of '['
        for r in range(rows):
            c = 0
            while c < cols:
                if warehouse[r][c] == '[':
                    total += 100 * r + c
                    c += 2  # Skip past the box
                else:
                    c += 1
    return total

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input = """########
#..O.O.#
##@.O..#
#...O..#
#.#.O..#
#...O..#
#......#
########

<^^>>>vv<v>>v<<
"""


    test_intput_2 = """##########
#..O..O.O#
#......O.#
#.OO..O.O#
#..O@..O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########

<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
"""

    test_input_3 = """#######
#...#.#
#.....#
#..OO@#
#..O..#
#.....#
#######

<vv<<^^<<^^
"""

    all_pass = True
    if part == 1:
        all_pass = all_pass and verify_result(part1(parse_input(test_input)), 2028, part)
        all_pass = all_pass and verify_result(part1(parse_input(test_intput_2)), 10092, part)

    if part == 2:
        #verify_result(part2(parse_input(test_input_3)), 9021, part)
        all_pass = all_pass and verify_result(part2(parse_input(test_intput_2)), 9021, part)
    return all_pass

if __name__ == "__main__":
    run_tests(15)
    run_day(15, part1=True, part2=True)
