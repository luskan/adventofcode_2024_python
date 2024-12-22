from typing import List, Tuple
from collections import defaultdict

from functools import cmp_to_key

from common import run_tests, run_day, verify_result

class ParsedData:
    __slots__ = ["towel_patterns", "desired_designs"]

    def __init__(self):
        self.towel_patterns: List[str] = []
        self.desired_designs: List[str] = []

def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    lines = data.strip().split('\n')
    if not lines:
        return result
    # First - towel patterns, separated by commas
    towel_patterns_line = lines[0]
    towel_patterns = [p.strip() for p in towel_patterns_line.split(',') if p.strip()]
    result.towel_patterns = towel_patterns

    desired_designs = []
    for j in range(1, len(lines)): # Desired designs are after one blank line
        if lines[j].strip() != '':
            desired_designs.append(lines[j].strip())
    result.desired_designs = desired_designs
    return result

# This function checks if a given design can be formed by concatenating the available patterns.
def can_form(design: str, patterns: List[str]) -> bool:
    n = len(design)

    # DP array dp where dp[i] indicates whether the first i characters of the design can be formed.
    dp = [False] * (n + 1)
    dp[0] = True  # Empty string can always be formed

    # For each position i in the design, it checks all patterns to see if any of them
    # match the substring ending at i. If a match is found and the preceding substring can be formed
    # (dp[i - plen] is True), then dp[i] is set to True.
    for i in range(1, n + 1):
        # Check each towel pattern if given design can be created
        for pattern in patterns:
            plen = len(pattern)
            if plen <= i and design[i - plen:i] == pattern:
                if dp[i - plen]:
                    dp[i] = True
                    break  # No need to check other patterns
    return dp[n]

# For each desired design, use DP to compute the number of ways it can be constructed
# by concatenating the available towel patterns.
def count_ways(design: str, patterns: List[str]) -> int:
    n = len(design)

    # dp[i] represents the number of ways to form the first i characters of the design
    dp = [0] * (n + 1)
    dp[0] = 1  # One way to form the empty string

    # For each position i in the design, iterate through all towel patterns and update dp[i] accordingly.
    for i in range(1, n + 1):
        for pattern in patterns:
            plen = len(pattern)
            if plen <= i and design[i - plen:i] == pattern:
                dp[i] += dp[i - plen]
    return dp[n]

def solver(data: ParsedData, part: int) -> int:
    result = 0
    patterns = data.towel_patterns
    designs = data.desired_designs
    if part == 1:
        # Count the number of designs that can be formed
        for design in designs:
            if can_form(design, patterns):
                result += 1
    elif part == 2:
        # Count the total number of ways across all designs
        for design in designs:
            ways = count_ways(design, patterns)
            if ways > 0:
                result += ways
    return result

def part1(data: ParsedData) -> int:
    return solver(data, 1)

def part2(data: ParsedData) -> int:
    return solver(data, 2)

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input = """
r, wr, b, g, bwu, rb, gb, br

brwrr
bggr
gbbr
rrbgbr
ubwu
bwurrg
brgr
bbrgwb
    """
    parsed_data = parse_input(test_input)
    all_pass = True

    if part == 1:
        result = part1(parsed_data)
        all_pass = all_pass and verify_result(result, 6, 1)
    elif part == 2:
        result = part2(parsed_data)
        all_pass = all_pass and verify_result(result, 16, 2)
    return all_pass

if __name__ == "__main__":
    run_tests(19)
    run_day(19, part1=True, part2=True)
