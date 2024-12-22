# main.py
import importlib
import time
import sys
import argparse

from common import get_expected_results, run_day, run_tests


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


def parse_args():
    parser = argparse.ArgumentParser(description='Advent of Code solution runner')
    parser.add_argument('days', type=int, nargs='*', help='Days to run (if not specified, run all days)')
    parser.add_argument('-t', '--test', action='store_true', help='Run only tests')
    return parser.parse_args()


def main():
    args = parse_args()

    # Determine which days to run
    days = args.days if args.days else range(1, 19)

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