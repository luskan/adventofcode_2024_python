import sys
from typing import List
import numpy as np

from common import verify_result, run_day, run_tests

import cProfile
import pstats

class ParsedData:
    __slots__ = ["numbers"]

    def __init__(self):
        self.numbers: List[int] = []

def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    result.numbers = [int(x) for x in data.strip().split('\n')]
    return result


def generate_steps(numbers: np.ndarray, steps: int) -> np.ndarray:
    """
    Generates all secret numbers for each initial number over a specified number of steps.
    :param numbers: Array of initial secret numbers.
    :param steps: Number of steps to generate.
    :return: np.ndarray: 2D array where each row corresponds to the secret number sequence for an initial number.
    """
    N = numbers.shape[0]
    steps_array = np.empty((N, steps), dtype=np.int64)
    secret_numbers = numbers.copy()
    for i in range(steps):
        # Apply the three transformation steps
        secret_numbers = ((secret_numbers * 64) ^ secret_numbers) % 16777216
        secret_numbers = ((secret_numbers // 32) ^ secret_numbers) % 16777216
        secret_numbers = ((secret_numbers * 2048) ^ secret_numbers) % 16777216
        steps_array[:, i] = secret_numbers
    return steps_array


def part1(data: ParsedData) -> int:
    numbers = np.array(data.numbers, dtype=np.int64)
    steps = 2000
    final_steps = generate_steps(numbers, steps)
    return int(final_steps[:, -1].sum())

def part2(data: ParsedData) -> int:
    """
        Solution uses NumPy vectorization with aggregation.
    """

    numbers = np.array(data.numbers, dtype=np.int64)
    N = len(numbers)
    steps = 2000
    steps_array = generate_steps(numbers, steps)

    # Compute prices (last digit of each secret number)
    prices = steps_array % 10  # Shape: (N, steps)

    # Compute diffs: difference between consecutive prices
    diffs = prices[:, 1:] - prices[:, :-1]  # Shape: (N, steps-1)

    # Number of 4-diff sequences per number
    num_sequences = steps - 4

    # Shift diffs to make them positive for encoding
    shifted_diffs = diffs + 10  # Range: 1 to 19

    # Encode each 4-diff sequence uniquely using base-19
    sequence_id = (
            shifted_diffs[:, 0:num_sequences] * (19 ** 3) +
            shifted_diffs[:, 1:num_sequences + 1] * (19 ** 2) +
            shifted_diffs[:, 2:num_sequences + 2] * 19 +
            shifted_diffs[:, 3:num_sequences + 3]
    )  # Shape: (N, num_sequences)

    # Corresponding banana counts are the prices at the 4th step of each sequence
    banana_counts = prices[:, 4:steps]  # Shape: (N, num_sequences)

    # Flatten the arrays for processing
    flat_seq_ids = sequence_id.flatten()
    flat_banana_counts = banana_counts.flatten()

    # Assign a unique identifier to each number
    number_ids = np.repeat(np.arange(N), num_sequences)

    # Combine number_id and sequence_id to ensure uniqueness per number
    combined_key = number_ids * (19 ** 4) + flat_seq_ids  # Assuming 19^4 < 2^32

    # Identify the first occurrence of each (number_id, sequence_id) pair
    unique_keys, unique_indices = np.unique(combined_key, return_index=True)
    first_banana_counts = flat_banana_counts[unique_indices]

    # Extract the original sequence_ids
    sequence_ids = unique_keys % (19 ** 4)

    # Aggregate banana counts for each sequence_id
    sum_banana = np.bincount(sequence_ids, weights=first_banana_counts, minlength=19 ** 4)

    if len(sum_banana) == 0:
        return 0
    return int(sum_banana.max())


def solve(data: str, part: int = 1):
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test(part) -> bool:
    test_input_part1 = """
1
10
100
2024
"""
    test_input_part2 = """
1
2
3
2024
"""
    all_pass = True
    if part == 1:
        expected = 37327623
        result = part1(parse_input(test_input_part1))
        all_pass &= verify_result(result, expected, part)
    if part == 2:
        expected = 23
        result = part2(parse_input(test_input_part2))
        all_pass &= verify_result(result, expected, part)
    return all_pass


if __name__ == "__main__":
    #profiler = cProfile.Profile()
    #profiler.enable()
    run_tests(22)
    run_day(22, part1=True, part2=True)
    #profiler.disable()
    #stats = pstats.Stats(profiler).sort_stats('cumtime')
    #stats.print_stats(10)  # Print top 10 slowest functions