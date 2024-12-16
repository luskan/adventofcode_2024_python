from typing import List, Tuple
from collections import defaultdict

from common import verify_result, run_day, run_tests
from functools import cmp_to_key

class ParsedData:
    __slots__ = ["machines"]
    def __init__(self):
        self.machines: List[Tuple[int, int, int, int, int, int]] = []  # (XA, YA, XB, YB, X_target, Y_target)

def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    blocks = data.strip().split('\n\n')
    for block in blocks:
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if len(lines) < 3:
            continue
        lineA = lines[0]
        lineB = lines[1]
        linePrize = lines[2]

        XA, YA = parse_button_line(lineA)
        XB, YB = parse_button_line(lineB)
        X_target, Y_target = parse_prize_line(linePrize)

        result.machines.append((XA, YA, XB, YB, X_target, Y_target))
    return result

def parse_button_line(line: str) -> Tuple[int, int]:
    parts = line.split(':', 1)[1].strip().split(',')
    x_part = parts[0].strip() # "X+NN"
    y_part = parts[1].strip() # "Y+NN"
    XA = int(x_part[1:])
    YA = int(y_part[1:])
    return (XA, YA)

def parse_prize_line(line: str) -> Tuple[int, int]:
    parts = line.split(':', 1)[1].strip().split(',')
    x_part = parts[0].strip() # "X=NNN"
    y_part = parts[1].strip() # "Y=NNN"
    X_target = int(x_part.split('=')[1])
    Y_target = int(y_part.split('=')[1])
    return (X_target, Y_target)

def part1(data: ParsedData) -> int:
    return solver(data, 1)

def part2(data: ParsedData) -> int:
    # Same as part1 excapt that we add 10^13 to each target coordinate.
    for i, (XA, YA, XB, YB, X_target, Y_target) in enumerate(data.machines):
        X_target += 10000000000000
        Y_target += 10000000000000
        data.machines[i] = (XA, YA, XB, YB, X_target, Y_target)

    return solver(data, 2)

def solver(data: ParsedData, part: int) -> int:
    total_cost = 0
    winners = 0

    for (XA, YA, XB, YB, X_target, Y_target) in data.machines:
        a, b = solve_machine(XA, YA, XB, YB, X_target, Y_target)
        if a is not None and b is not None and a >= 0 and b >= 0:
            cost = 3*a + b
            winners += 1
            total_cost += cost

    return total_cost

def solve_machine(XA: int, YA: int, XB: int, YB: int, X_target: int, Y_target: int) -> Tuple:
    # Solve the system of equations:
    # XA*a + XB*b = X_target
    # YA*a + YB*b = Y_target
    #
    # Using Cramer's rule:
    det = XA*YB - XB*YA
    if det == 0:
        return None, None

    # Check if we have integer solutions
    detA = X_target*YB - XB*Y_target
    detB = XA*Y_target - X_target*YA

    # For a and b to be integers, detA and detB must be divisible by det
    if (detA % det != 0) or (detB % det != 0):
        return None, None

    a = detA // det
    b = detB // det
    return a, b

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input = """
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279
"""
    parsed_data = parse_input(test_input)
    if part == 1:
        return verify_result(part1(parsed_data), 480, 1)
    else:
       # no expected result for part 2 provided
       pass;

    return True

if __name__ == "__main__":
    run_tests(13)
    run_day(13, part1=True, part2=True)
