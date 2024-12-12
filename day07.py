from itertools import product
from operator import truediv
from typing import List

from common import verify_result, run_day, run_tests


class Equation:
    __slots__ = ["lhs", "rhs"]
    def __init__(self):
        self.lhs: int = 0
        self.rhs: List[int] = []


class ParsedData:
    __slots__ = ["equations"]
    def __init__(self):
        self.equations: List[Equation] = []


def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    for line in data.split('\n'):
        line = line.strip()
        if not line:
            continue
        equation = Equation()
        lhs, rhs = line.split(":")
        equation.lhs = int(lhs)
        equation.rhs = list(map(int, rhs.split()))
        result.equations.append(equation)
    return result


def part1(data: ParsedData) -> int:
    return solver(data, 1)


def part2(data: ParsedData) -> int:
    return part_two_v2(data)
    # bruteforce, very slow - ~20s
    #return solver(data, 2)

def concat(a, b):
    """Concatenate two integers a and b."""
    # Find the number of digits in b
    if b == 0:
        return a * 10
    offset = 1
    while b >= offset:
        offset *= 10
    return a * offset + b

# Idea found on reddit forum
# It recursively evaluates the expression by trying to add or multiply the next number
def recurse_evaluate(start, target, numbers, index=0):
    if start > target:
        return False

    if index == len(numbers):
        return start == target

    first = numbers[index]

    if recurse_evaluate(start + first, target, numbers, index + 1):
        return True
    if recurse_evaluate(start * first, target, numbers, index + 1):
        return True

    if first == 0:
        concat_val = start * 10
    else:
        offset = 1
        while first >= offset:
            offset *= 10
        concat_val = start * offset + first

    return recurse_evaluate(concat_val, target, numbers, index + 1)

def part_two_v2(equations: ParsedData):
    """Solve part two using +, *, and concatenation with dynamic programming."""
    total = 0
    for eq in equations.equations:
        target, numbers = eq.lhs, eq.rhs
        start = numbers[0]
        rest = numbers[1:]
        if recurse_evaluate(start, target, rest):
            total += target
    return total


def solver(data: ParsedData, part: int) -> int:
    operators = '+*' if part == 1 else '+*|'

    # Precompute all possible combinations for each operand count encountered
    # to avoid regenerating them for each equation.
    operand_counts = set(len(eq.rhs) - 1 for eq in data.equations)
    combinations_cache = {}
    for count in operand_counts:
        if count >= 0:
            combinations_cache[count] = [''.join(p) for p in product(operators, repeat=count)]

    result = 0

    for eq in data.equations:
        number_of_operands = len(eq.rhs) - 1
        combinations = combinations_cache[number_of_operands]
        lhs_val = eq.lhs
        rhs_list = eq.rhs

        # Try each combination until we find one that matches eq.lhs
        for comb in combinations:
            test_sum = rhs_list[0]
            match = True
            for i, op in enumerate(comb, start=1):
                rhs_val = rhs_list[i]
                if op == '+':
                    test_sum += rhs_val
                elif op == '*':
                    test_sum *= rhs_val
                else:
                    # '|' operation: concatenate numbers
                    test_sum = concat(test_sum, rhs_val)
                if test_sum > lhs_val:
                    break

            if test_sum == lhs_val:
                result += test_sum
                break

    return result


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test(part) -> None:
    test_input = """
190: 10 19
3267: 81 40 27
83: 17 5
156: 15 6
7290: 6 8 6 15
161011: 16 10 13
192: 17 8 14
21037: 9 7 18 13
292: 11 6 16 20
"""
    parsed_data = parse_input(test_input)
    all_pass = True
    if part == 1:
        all_pass = verify_result(part1(parsed_data), 3749, 1) and all_pass
    if part == 2:
        all_pass = verify_result(part2(parsed_data), 11387, 2) and all_pass
    return all_pass


if __name__ == "__main__":
    run_tests(7)
    run_day(7, part1=True, part2=True)
