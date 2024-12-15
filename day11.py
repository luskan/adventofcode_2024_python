from common import verify_result, run_day, run_tests

class ParsedData:
    __slots__ = ["line"]

    def __init__(self):
        self.line: str = ""


def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    result.line = ' '.join(data.strip().split())
    return result


def part1(data: ParsedData, blinks: int = 25) -> int:
    return solver(data, blinks)


def solver(data: ParsedData, blinks: int) -> int:
    initial_numbers = list(map(int, data.line.split()))

    memo = {}

    def count_stones(num: int, remaining_blinks: int) -> int:
        if remaining_blinks == 0:
            return 1
        key = (num, remaining_blinks)
        if key in memo:
            return memo[key]

        if num == 0:
            # rule 1: Replace 0 with 1
            result = count_stones(1, remaining_blinks - 1)
        elif len(str(num)) % 2 == 0:
            # rule 2: Split into two stones
            num_str = str(num)
            half = len(num_str) // 2
            left_str = num_str[:half].lstrip('0') or '0'
            right_str = num_str[half:].lstrip('0') or '0'
            left_num = int(left_str)
            right_num = int(right_str)
            result = count_stones(left_num, remaining_blinks - 1) + count_stones(right_num, remaining_blinks - 1)
        else:
            # rule 3: Multiply by 2024
            new_num = num * 2024
            result = count_stones(new_num, remaining_blinks - 1)

        memo[key] = result
        return result

    total = 0
    for num in initial_numbers:
        total += count_stones(num, blinks)

    return total


def part2(data: ParsedData) -> int:
    return solver(data, 75)


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> None:
    test_input = """
0 1 10 99 999
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    # Test part 1
    if (part == 1):
        all_pass = all_pass and verify_result(part1(parsed_data), 125681, 1) # thats not in the problem description
        all_pass = all_pass and verify_result(part1(parse_input("125 17"), blinks=6), 22, 1)
        all_pass = all_pass and verify_result(part1(parse_input("125 17"), blinks=25), 55312, 1)

    return all_pass

if __name__ == "__main__":
    #run_tests(11)
    run_day(11, part1=True, part2=True)
