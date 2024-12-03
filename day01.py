from typing import List, Tuple

ParsedData = Tuple[List[int], List[int]]

def parse_input(data: str) -> ParsedData:
    col1, col2 = [], []
    for line in data.split('\n'):
        if line.strip():
            num1, num2 = map(int, line.split())
            col1.append(num1)
            col2.append(num2)
    return col1, col2


def part1(data: ParsedData) -> int:
    data[0].sort()
    data[1].sort()

    sum = 0

    for i in range(len(data[0])):
        sum += abs(data[0][i] - data[1][i])

    return sum


def part2(data: ParsedData) -> int:
    data[0].sort()
    data[1].sort()

    sum = 0

    for i in range(len(data[0])):
        sum += abs(data[0][i] * data[1].count(data[0][i]))

    return sum


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test() -> None:
    test_input = """
3   4
4   3
2   5
1   3
3   9
3   3
"""

    parsed_data = parse_input(test_input)

    # Test part 1
    assert part1(parsed_data) == 11, "Part 1 test failed"
    print("Part 1 tests passed!")

    # Test part 2
    assert part2(parsed_data) == 31, "Part 2 test failed"
    print("Part 2 tests passed!")
