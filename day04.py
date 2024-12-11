from typing import List, Tuple

from common import verify_result

ParsedData = List[str]

def parse_input(data: str) -> ParsedData:
    result: ParsedData = []
    for line in data.split('\n'):
        if line.strip():
            result.append(line)
    return result


def count_patterns(text: str, patterns) -> int:
    count = 0

    for pattern in patterns:
        # Check each possible starting position
        for i in range(len(text) - len(pattern) + 1):
            if text[i:i + len(pattern)] == pattern:
                count += 1

    return count


def check_pattern(data, x, y, patterns) -> int:
    result = 0
    width = len(data[0])
    height = len(data)
    for pattern in patterns:
        success = True
        for yp in range(len(pattern)):
            for xp in range(len(pattern[yp])):
                if pattern[yp][xp] == "#":
                    continue
                if x + xp >= width or y + yp >= height:
                    success = False
                    break
                if data[y + yp][x + xp] != pattern[yp][xp]:
                    success = False
                    break
        result += 1 if success else 0
    return result

def part1(data: ParsedData) -> int:
    return solver(data, 1)

def solver(data: ParsedData, part: int) -> int:
    result = 0

    patterns = [
        ["XMAS"],
        ["SAMX"],
        [
            "X",
            "M",
            "A",
            "S"
        ],
        [
            "S",
            "A",
            "M",
            "X"
        ],
        [
            "X###",
            "#M##",
            "##A#",
            "###S"
        ],
        [
            "S###",
            "#A##",
            "##M#",
            "###X"
        ],
        [
            "###X",
            "##M#",
            "#A##",
            "S###"
        ],
        [
            "###S",
            "##A#",
            "#M##",
            "X###"
        ]
    ]

    patterns2 = [
        [
            "M#S",
            "#A#",
            "M#S",
        ],
        [
            "M#M",
            "#A#",
            "S#S",
        ],
        [
            "S#M",
            "#A#",
            "S#M",
        ],
        [
            "S#S",
            "#A#",
            "M#M",
        ]
    ]

    for x in range(0, len(data[0])):
        for y in range(0, len(data)):
            result += check_pattern(data, x, y, patterns if part == 1 else patterns2)

    return result


# First try was to rotate data - but it does not work, rotations look to be ok
def part1_rot(data: ParsedData) -> int:
    result = 0

    patterns = ["XMAS", "SAMX"]

    width = len(data[0])
    height = len(data)

    # Find number of patterns in each row
    for i in range(height):
        result += count_patterns(data[i], patterns)

    # Find number of patterns in each column
    for j in range(width):
        col = "".join([data[k][j] for k in range(height)])
        result += count_patterns(col, patterns)

    # Rotate data -45 degrees
    max_diagonal = width + height - 1
    mid = width - 1  # Reference point for centering
    rotated_data = [""] * max_diagonal

    for i in range(height):
        for j in range(width):
            # Calculate rotated position
            new_pos = (j - i) + mid
            if 0 <= new_pos < max_diagonal:
                rotated_data[new_pos] += data[i][j]

    # Print rotated data for debugging
    for line in rotated_data:
        print(line)

    # Find number of patterns in each line of rotated data
    for i in range(len(rotated_data)):
        result += count_patterns(rotated_data[i], patterns)

    # Find number of patterns in each column of rotated data
    max_length = max(len(row) for row in rotated_data)
    padded_rotated_data = [row.ljust(max_length, " ") for row in rotated_data]

    for col_idx in range(max_length):
        column = "".join(row[col_idx] for row in padded_rotated_data if col_idx < len(row))
        result += count_patterns(column, patterns)

    return result


def part2(data: ParsedData) -> int:
    return solver(data, 2)


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test(part) -> None:
    test_input = """
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    # Test part 1
    if part == 1:
        all_pass = all_pass and verify_result(part1(parsed_data), 18, 1)

    # Test part 2
    if part == 2:
        all_pass = all_pass and verify_result(part2(parsed_data), 9, 2)

    return all_pass