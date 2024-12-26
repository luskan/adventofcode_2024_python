import sys
from typing import List, Tuple
from collections import defaultdict

from common import verify_result, run_day, run_tests
# from functools import cmp_to_key  # Removed since it's unused

class ParsedData:
    __slots__ = ["numbers"]

    def __init__(self):
        self.numbers: List[int] = []

def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    result.numbers = [int(x) for x in data.strip().split('\n')]
    return result

def next_number(secret_number: int) -> int:
    secret_number = ((secret_number * 64) ^ secret_number) % 16777216
    secret_number = ((secret_number // 32) ^ secret_number) % 16777216
    secret_number = ((secret_number * 2048) ^ secret_number) % 16777216
    return secret_number

def calculate_secret_number(secret_number: int, steps: int) -> int:
    for _ in range(steps):
        secret_number = next_number(secret_number)
    return secret_number

def part1(data: ParsedData) -> int:
    return sum(calculate_secret_number(num, 2000) for num in data.numbers)

def part2(data: ParsedData) -> int:
    # collect sequences and their summed banana_counts
    sequences_count = defaultdict(int)

    for initial_number in data.numbers:
        diffs = []
        cur_sec = initial_number

        for _ in range(2000):
            prev_sec = cur_sec
            cur_sec = next_number(cur_sec)
            diff = (cur_sec % 10) - (prev_sec % 10)
            diffs.append((cur_sec % 10, diff))

        # Build the dictionary for 4-diff sequences -> first banana count found
        seq_dict = {}
        for i in range(3, len(diffs)):
            banana_count = diffs[i][0]
            seq = (
                diffs[i - 3][1],
                diffs[i - 2][1],
                diffs[i - 1][1],
                diffs[i][1],
            )
            if seq not in seq_dict:
                seq_dict[seq] = banana_count

        # Update global counts
        for seq, count in seq_dict.items():
            sequences_count[seq] += count

    max_value = max(sequences_count.values()) if sequences_count else 0
    return max_value

def solve(data: str, part: int = 1):
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input = """
1
10
100
2024
"""
    test_input2 = """
1
2
3
2024
"""
    all_pass = True
    if part == 1:
        all_pass &= verify_result(part1(parse_input(test_input)), 37327623, 1)
    if part == 2:
        all_pass &= verify_result(part2(parse_input(test_input2)), 23, 2)
    return all_pass

if __name__ == "__main__":
    run_tests(22)
    run_day(22, part1=True, part2=True)
