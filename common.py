import importlib
import time
from pathlib import Path


def verify_result(actual, expected, part):
    """Verify if the actual result matches the expected result."""
    if expected is None:
        return "❓ (no expected result)"

    if str(actual) == str(expected):
        print(f"✅ {actual}")
        return True
    else:
        print(f"❌ Got: {actual}, Expected: {expected}")
        #exit(1)
        return False

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


def run_tests(day_num: int) -> bool:
    """Run tests for a specific day."""
    try:
        day_module = importlib.import_module(f"day{day_num:02d}")
        print(f"\nRunning tests for Day {day_num}: ")
        print("Part 1: ", end="")
        part1_passed = day_module.test(1)
        print("Part 2: ", end="")
        part2_passed = day_module.test(2)
        return part1_passed and part2_passed
    except ImportError:
        print(f"Day {day_num} not implemented yet")
        return False
    #except Exception as e:
     #   print(f"Error running tests for day {day_num}: {e}")
     #   return False


def run_day(day_num: int, part1: bool = True, part2: bool = True) -> bool:
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
        part1_passed, part2_passed = True, True
        if part1:
            print("Part 1: ", end="")
            part1_result = day_module.solve(data, part=1)
            part1_passed = verify_result(part1_result, expected_part1, 1)
        if part2:
            print("Part 2: ", end="")
            part2_result = day_module.solve(data, part=2)
            part2_passed = verify_result(part2_result, expected_part2, 2)

        end_time = time.time()
        print(f"Time: {(end_time - start_time) * 1000:.2f}ms")
        return part1_passed and part2_passed

    except ImportError:
        print(f"Day {day_num} not implemented yet")
        return False
