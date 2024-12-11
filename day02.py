from typing import List, Tuple

from common import verify_result

ParsedData = List[List[int]]

def parse_input(data: str) -> ParsedData:
    parsedData = []
    for line in data.split('\n'):
        if line.strip():
            numbers = list(map(int, line.split()))
            parsedData.append(numbers)
    return parsedData

def signum(x: int) -> int:
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def part1(data: ParsedData) -> int:
    safe_reports = 0

    for i in range(len(data)):
        last_change = data[i][1] - data[i][0]
        safe = True
        for m in range(1, len(data[i])):
            change = data[i][m] - data[i][m-1]
            if abs(change) > 3 or change == 0 or signum(change) != signum(last_change):
                safe = False
                break
        if safe:
            safe_reports += 1

    return safe_reports


def part2(data: ParsedData) -> int:
    safe_reports = 0

    for i in range(len(data)):
        vec = data[i]
        is_safe = False
        for im in range(-1, len(vec)):
            vec_cpy = vec.copy()
            if im != -1:
                vec_cpy.pop(im)

            last_change = vec_cpy[1] - vec_cpy[0]
            safe = True
            for m in range(1, len(vec_cpy)):
                change = vec_cpy[m] - vec_cpy[m-1]
                if abs(change) > 3 or change == 0 or signum(change) != signum(last_change):
                    safe = False
                    break
            if safe:
                is_safe = True
                break
        if is_safe:
            safe_reports += 1

    return safe_reports


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test(part) -> bool:
    test_input = """
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9
"""

    parsed_data = parse_input(test_input)
    all_pass = True

    if part == 1:
        # Test part 1
        all_pass = all_pass and verify_result(part1(parsed_data), 2, 1)

    if part == 2:
        # Test part 2
        all_pass = all_pass and verify_result(part2(parsed_data), 4, 2)

    return all_pass
