from typing import List, Tuple
from collections import defaultdict

from common import verify_result
from functools import cmp_to_key

# Class
class ParsedData:
    Rule = Tuple[int, int]
    Update = List[int]

    def __init__(self):
        self.rules: List[ParsedData.Rule] = []
        self.updates: List[ParsedData.Update] = []


def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    parsing_rules = True
    for line in data.split('\n'):
        if line.strip() == "" and len(result.rules) != 0:
            parsing_rules = False
            continue
        if line.strip() == "":
            continue
        if parsing_rules:
            rule = tuple(map(int, line.split("|")))
            result.rules.append(rule)
        else:
            update = list(map(int, line.split(",")))
            result.updates.append(update)
    return result


def part1(data: ParsedData) -> int:
    return solver(data, 1)


def is_correctly_ordered(data: ParsedData.Update, rules_set_nums: set, rules_map) -> bool:
    for i1 in range(len(data)):
        page1 = data[i1]
        if page1 not in rules_set_nums:
            continue
        for i2 in range(i1 + 1, len(data)):
            page2 = data[i2]
            if page2 not in rules_set_nums:
                continue
            if page1 not in rules_map.get(page2, []):
                return False
    return True


def custom_compare(elem1, elem2, rules_map):
    if elem2 in rules_map.get(elem1, []):
        return 1
    if elem1 in rules_map.get(elem2, []):
        return -1
    return 0


def solver(data: ParsedData, part: int) -> int:
    rule_id = 0
    result = 0

    rules_set_nums = set()
    for rule in data.rules:
        rules_set_nums.add(rule[0])
        rules_set_nums.add(rule[1])

    # Precompute a multimap for rules
    rules_map = defaultdict(list)
    for rule in data.rules:
        rules_map[rule[1]].append(rule[0])  # Map each page to all preceding pages

    for update in data.updates:
        add_result = False
        is_correct_order = is_correctly_ordered(update, rules_set_nums, rules_map)
        if is_correct_order:
            add_result = True if part == 1 else False

        if not is_correct_order and part == 2:
            update.sort(key=cmp_to_key(lambda x, y: custom_compare(x, y, rules_map)))
            add_result = True

        if add_result:
            if len(update) % 2 == 0:
                result += update[len(update)//2 - 1]
            else:
                result += update[len(update)//2]
        rule_id += 1
    return result


def part2(data: ParsedData) -> int:
    return solver(data, 2)


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test() -> None:
    test_input = """
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47
"""

    parsed_data = parse_input(test_input)

    # Test part 1
    verify_result(part1(parsed_data), 143, 1)
    print("Part 1 tests passed!")

    # Test part 2
    verify_result(part2(parsed_data), 123, 2)
    print("Part 2 tests passed!")
