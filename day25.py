from multiprocessing.managers import Value
from typing import List, Tuple
from collections import defaultdict

from common import verify_result, run_day, run_tests
from functools import cmp_to_key

class ParsedData:
    __slots__ = ["locks", "keys"]

    def __init__(self):
        self.locks: List[List[int]] = []
        self.keys: List[List[int]] = []

def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    nums: List[int] = [0 for i in range(5)]
    skip_first_line = True
    current_is_lock = -1
    for line in data.split('\n'):
        if line.strip() == "":
            if current_is_lock == -1:
                continue
            if current_is_lock == 1:
                result.locks.append(nums.copy())
            elif current_is_lock == 0:
                result.keys.append([k - 1 for k in nums])

            for n in range(5):
                nums[n] = 0
            skip_first_line = True
            current_is_lock = -1

        else:
            if skip_first_line:
                skip_first_line = False
                if line.count("#") == 5:
                    current_is_lock = 1
                elif line.count(".") == 5:
                    current_is_lock = 0
                else:
                    raise ValueError("Unknown line")
            else:
                for i, c in enumerate(line):
                    nums[i] = nums[i] + (1 if c == "#" else 0)

    if current_is_lock == 1:
        result.locks.append(nums)
    elif current_is_lock == 0:
        result.keys.append(nums)

    return result

def part1(data: ParsedData) -> int:
    return solver(data, 1)

def solver(data: ParsedData, part: int) -> int:
    result = 0

    for key in data.keys:
        for lock in data.locks:
            sum = 0
            for n in range(5):
                sum += 1 if (key[n] + lock[n]) <= 5 else 0
            if sum == 5:
                result += 1

    return result

def part2(data: ParsedData) -> int:
    return solver(data, 2)

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input = """
#####
.####
.####
.####
.#.#.
.#...
.....

#####
##.##
.#.##
...##
...#.
...#.
.....

.....
#....
#....
#...#
#.#.#
#.###
#####

.....
.....
#.#..
###..
###.#
###.#
#####

.....
.....
.....
#....
#.#..
#.#.#
#####
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    # Test part 1
    if (part == 1):
        all_pass = all_pass and verify_result(part1(parsed_data), 3, 1)

    # Test part 2
    #if (part == 2):
    #    all_pass = all_pass and verify_result(part2(parsed_data), 0, 2)

    return all_pass

if __name__ == "__main__":
    run_tests(25)
    run_day(25, part1=True, part2=False)
