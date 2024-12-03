import re
from typing import List, Tuple

ParsedData = List[List[int]]

def parse_input(data: str) -> ParsedData:
    parsedData = []
    for line in data.split('\n'):
        matches = re.findall(r'mul\((\d+),(\d+)\)', line)
        for match in matches:
            numbers = list(map(int, match))
            parsedData.append(numbers)

    return parsedData

def parse_input2(data: str) -> ParsedData:
    parsedData = []
    allow_mul = True
    for line in data.split('\n'):
        matches = re.findall(r'(do\(\))|(don\'t\(\))|mul\((\d+),(\d+)\)', line)
        for match in matches:
            if match[0] == 'do()' :
                allow_mul = True
                continue
            if match[1] == 'don\'t()':
                    allow_mul = False
                    continue
            if not allow_mul:
                continue
            numbers = [int(match[2]), int(match[3])]
            parsedData.append(numbers)

    return parsedData

def part1(data: ParsedData) -> int:
    sum = 0
    for i in range(len(data)):
        sum += data[i][0] * data[i][1]
    return sum


def part2(data: ParsedData) -> int:
    sum = 0
    for i in range(len(data)):
        sum += data[i][0] * data[i][1]
    return sum # 192767529 too high


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data) if part == 1 else parse_input2(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test() -> None:
    # Test part 1
    test_input = """
xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))
"""
    parsed_data = parse_input(test_input)
    assert part1(parsed_data) == 161, "Part 1 test failed"
    print("Part 1 tests passed!")

    # Test part 2
    test_input = """
xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
"""
    parsed_data = parse_input2(test_input)
    assert part2(parsed_data) == 48, "Part 2 test failed"
    print("Part 2 tests passed!")
