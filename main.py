# main.py
import importlib
import time
from pathlib import Path
import sys
import argparse


# Directory structure:
# /
# ├── main.py
# ├── day01.py
# ├── day02.py
# ├── ..
# └── day25.py

# Input files:
# ../adventofcode_input/2024/data/
#     ├── day01.txt
#     ├── day01_result.txt
#     ├── day02.txt
#     ├── day02_result.txt
#     ├── ...
#     ├── day25.txt
#     └── day25_test.txt

def get_expected_results(day_num: int):
    """Get expected results from result file."""
    result_file = Path(f"../adventofcode_input/2024/data/day{day_num:02d}_result.txt")
    if not result_file.exists():
        return None, None

    try:
        lines = result_file.read_text().strip().split('\n')
        return (lines[0].strip(), lines[1].strip()) if len(lines) >= 2 else (lines[0].strip(), None)
    except Exception:
        return None, None


def verify_result(actual, expected, part_num):
    """Verify if the actual result matches the expected result."""
    if expected is None:
        return "❓ (no expected result)"

    actual_str = str(actual)
    if actual_str == expected:
        return f"✅ {actual}"
    else:
        return f"❌ Got: {actual}, Expected: {expected}"


def run_day(day_num: int):
    try:
        day_module = importlib.import_module(f"day{day_num:02d}")
        input_file = Path(f"../adventofcode_input/2024/data/day{day_num:02d}.txt")
        if not input_file.exists():
            print(f"No input file found for day {day_num}")
            return False

        data = input_file.read_text().strip()
        expected_part1, expected_part2 = get_expected_results(day_num)

        start_time = time.time()

        # Run both parts and verify results
        print(f"\nDay {day_num}:")
        part1_result = day_module.solve(data, part=1)
        part2_result = day_module.solve(data, part=2)

        print(f"Part 1: {verify_result(part1_result, expected_part1, 1)}")
        print(f"Part 2: {verify_result(part2_result, expected_part2, 2)}")

        end_time = time.time()
        print(f"Time: {(end_time - start_time) * 1000:.2f}ms")

        # Return True if both parts match expected results
        return (expected_part1 is None or str(part1_result) == expected_part1) and \
            (expected_part2 is None or str(part2_result) == expected_part2)

    except ImportError:
        print(f"Day {day_num} not implemented yet")
        return False
    #except Exception as e:
     #   print(f"Error running day {day_num}: {e}")
      #  return False


def run_tests(day_num: int):
    """Run tests for a specific day."""
    try:
        day_module = importlib.import_module(f"day{day_num:02d}")
        print(f"\nRunning tests for Day {day_num}:")
        day_module.test()
        return True
    except ImportError:
        print(f"Day {day_num} not implemented yet")
        return False
    #except Exception as e:
     #   print(f"Error running tests for day {day_num}: {e}")
     #   return False


def parse_args():
    parser = argparse.ArgumentParser(description='Advent of Code solution runner')
    parser.add_argument('days', type=int, nargs='*', help='Days to run (if not specified, run all days)')
    parser.add_argument('-t', '--test', action='store_true', help='Run only tests')
    return parser.parse_args()


def main():
    args = parse_args()

    # Determine which days to run
    days = args.days if args.days else range(1, 6)

    # Track overall success
    all_passed = True

    start_time = time.time()

    # Run specified days
    for day in days:

        tests_passed = run_tests(day)
        all_passed = all_passed and tests_passed

        if not args.test:  # Skip actual solutions if --test flag is used
            day_passed = run_day(day)
            all_passed = all_passed and day_passed

    # Show final status
    end_time = time.time()
    print(f"\nTotal Time: {(end_time - start_time) * 1000:.2f}ms")
    status = "✅ All tests and solutions passed!" if all_passed else "❌ Some tests or solutions failed"
    print(f"Final Status: {status}")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()