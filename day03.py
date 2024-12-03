import re
from typing import List, Tuple, Optional
from dataclasses import dataclass
from collections import namedtuple

# Custom types for better readability and type safety
Multiplication = namedtuple('Multiplication', ['x', 'y'])
ParsedData = List[Multiplication]


def parse_input(data: str) -> ParsedData:
    parsed_data = []
    pattern = r'mul\((\d+),\s*(\d+)\)'

    try:
        matches = re.finditer(pattern, data, re.MULTILINE)
        for match in matches:
            x, y = map(int, match.groups())
            parsed_data.append(Multiplication(x, y))
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")

    return parsed_data


def parse_input2(data: str) -> ParsedData:
    parsed_data = []
    allow_mul = True
    pattern = r'(do\(\))|(don\'t\(\))|mul\((\d+),\s*(\d+)\)'

    try:
        matches = re.finditer(pattern, data, re.MULTILINE)
        for match in matches:
            do_cmd, dont_cmd, num1, num2 = match.groups()

            if do_cmd:
                allow_mul = True
                continue
            if dont_cmd:
                allow_mul = False
                continue

            if allow_mul and num1 and num2:
                x, y = map(int, (num1, num2))
                parsed_data.append(Multiplication(x, y))

    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")

    return parsed_data


def part1(data: ParsedData) -> int:
   return sum(mul.x * mul.y for mul in data)

def part2(data: ParsedData) -> Optional[int]:
    result = sum(mul.x * mul.y for mul in data)
    return result

def solve(data: str, part: int = 1) -> Optional[int]:
    if part not in (1, 2):
        raise ValueError("Part must be 1 or 2")

    parser = parse_input if part == 1 else parse_input2
    solver = part1 if part == 1 else part2

    try:
        parsed_data = parser(data)
        return solver(parsed_data)
    except (ValueError, TypeError) as e:
        raise RuntimeError(f"Failed to solve part {part}: {str(e)}")


def test() -> None:
    # Test part 1
    test_input = """
    xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))
    """
    parsed_data = parse_input(test_input)
    result = part1(parsed_data)
    assert result == 161, f"Part 1 test failed: expected 161, got {result}"
    print("Part 1 tests passed!")

    # Test part 2
    test_input = """
    xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
    """
    parsed_data = parse_input2(test_input)
    result = part2(parsed_data)
    assert result == 48, f"Part 2 test failed: expected 48, got {result}"
    print("Part 2 tests passed!")