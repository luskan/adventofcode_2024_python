from typing import List, Tuple
from collections import defaultdict

from common import verify_result, run_day
from functools import cmp_to_key

# Class
class ParsedData:
    __slots__ = ["line"]

    def __init__(self):
        self.line: str = ""

def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    result.line = data
    return result

def part1(data: ParsedData) -> int:
    return solver(data, 1)

def solver(data: ParsedData, part: int) -> int:
    result = 0
    return result

def part2(data: ParsedData) -> int:
    return solver(data, 2)

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input = """
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    # Test part 1
    if (part == 1):
        all_pass = all_pass and verify_result(part1(parsed_data), 0, 1)

    # Test part 2
    if (part == 2):
        all_pass = all_pass and verify_result(part2(parsed_data), 0, 2)

    return all_pass

#if __name__ == "__main__":
    #run_day(7, part1=False, part2=True)
