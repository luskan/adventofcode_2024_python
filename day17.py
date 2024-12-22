import sys
from typing import List, Tuple, Optional
from common import run_tests, run_day, verify_result
from day17_translator import translate_to_python

# Opcode to operation name mapping
OPCODE_MAPPING = {
    0: 'adv',   # Advance
    1: 'bxl',   # Bitwise XOR on Register B
    2: 'bst',   # Bitwise AND on Register B with modulo 8
    3: 'jnz',   # Jump if Not Zero
    4: 'bxc',   # Bitwise XOR between Register B and C
    5: 'out',   # Output
    6: 'bdv',   # Bitwise Division on Register B
    7: 'cdv',   # Bitwise Division on Register C
    # Extend this mapping if there are more opcodes
}

class ParsedData:
    __slots__ = ["register_a", "register_b", "register_c", "program"]

    def __init__(self):
        self.register_a: int = 0
        self.register_b: int = 0
        self.register_c: int = 0
        self.program: List[int] = []


def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    lines = data.strip().splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("Register A:"):
            result.register_a = int(line.split(":")[1].strip())
        elif line.startswith("Register B:"):
            result.register_b = int(line.split(":")[1].strip())
        elif line.startswith("Register C:"):
            result.register_c = int(line.split(":")[1].strip())
        elif line.startswith("Program:"):
            program_str = line.split(":")[1].strip()
            if program_str:
                result.program = [int(x) for x in program_str.split(",")]
            else:
                result.program = []
    return result


def print_readable_program(program: List[int], opcode_map: dict) -> None:
    """
    Prints the program instructions in a human-readable format.
    """
    print("Readable Program Instructions:")
    print("--------------------------------")
    i = 0
    program_length = len(program)
    while i < program_length:
        opcode = program[i]
        operation = opcode_map.get(opcode, f'unknown_opcode_{opcode}')

        # Each opcode is expected to be followed by one operand
        if i + 1 < program_length:
            operand = program[i + 1]
            print(f"{operation} {operand}")
            i += 2  # Move to the next opcode
        else:
            # Handle case where operand is missing
            print(f"{operation} [Missing Operand]")
            i += 1
    print("--------------------------------\n")


def execute_program(program: List[int], initial_a: int, initial_b: int, initial_c: int, max_steps: int = 1000000, return_on_out: bool = False) -> Optional[List[int]]:
    # 'combo' means the operand is a combo operand
    # 'literal' means the operand is a literal operand
    # 'ignored' means the operand is read but ignored
    opcode_operand_type = {
        0: 'combo',     # adv
        1: 'literal',   # bxl
        2: 'combo',     # bst
        3: 'literal',   # jnz
        4: 'ignored',   # bxc
        5: 'combo',     # out
        6: 'combo',     # bdv
        7: 'combo',     # cdv
    }

    # Initialize registers
    registers = {'A': initial_a, 'B': initial_b, 'C': initial_c}

    # Initialize instruction pointer and output list
    ip = 0  # Instruction Pointer
    output = []
    steps = 0

    while ip < len(program) and steps < max_steps:
        opcode = program[ip]

        # Check if operand exists
        if ip + 1 >= len(program):
            print(f"halt at: {ip} (Missing Operand)")
            break  # Halt if operand is missing

        operand = program[ip + 1]

        # Determine operand type
        operand_type = opcode_operand_type.get(opcode, None)  # Default to 'literal' if unknown
        if operand_type is None:
            raise ValueError(f"Unknown opcode: {opcode}")

        # Function to get operand value based on its type
        def get_operand_value(op, op_type):
            if op_type == 'literal':
                return op
            elif op_type == 'combo':
                if 0 <= op <= 3:
                    return op
                elif op == 4:
                    return registers['A']
                elif op == 5:
                    return registers['B']
                elif op == 6:
                    return registers['C']
                else:
                    raise ValueError(f"Invalid combo operand: {op}")
            elif op_type == 'ignored':
                # For bxc : "For legacy reasons, this instruction reads an operand but ignores it."
                return None
            else:
                raise ValueError(f"Unknown operand type: {op_type}")

        # Get the operand value
        try:
            operand_value = get_operand_value(operand, operand_type)
        except ValueError as e:
            print(f"Error: {e}")
            return None

        # Execute the instruction based on opcode
        if opcode == 0:  # adv
            denominator = 2 ** operand_value
            if denominator == 0:
                registers['A'] = 0  # Handle division by zero gracefully
            else:
                registers['A'] = registers['A'] // denominator
            ip += 2
        elif opcode == 1:  # bxl
            registers['B'] = registers['B'] ^ operand_value
            ip += 2
        elif opcode == 2:  # bst
            registers['B'] = operand_value % 8
            ip += 2
        elif opcode == 3:  # jnz
            if registers['A'] != 0:
                ip = operand_value
            else:
                ip += 2

        elif opcode == 4:  # bxc
            registers['B'] = registers['B'] ^ registers['C']
            ip += 2
        elif opcode == 5:  # out
            output_value = operand_value % 8
            if return_on_out:
                return [output_value]
            output.append(output_value)
            ip += 2
        elif opcode == 6:  # bdv
            denominator = 2 ** operand_value
            if denominator == 0:
                registers['B'] = 0  # Handle division by zero gracefully
            else:
                registers['B'] = registers['A'] // denominator
            ip += 2
        elif opcode == 7:  # cdv
            denominator = 2 ** operand_value
            if denominator == 0:
                registers['C'] = 0  # Handle division by zero gracefully
            else:
                registers['C'] = registers['A'] // denominator
            ip += 2
        else:
            # Unknown opcode, halt
            print(f"Unknown opcode {opcode} at position {ip}. Halting.")
            break

        steps += 1

    if steps >= max_steps:
        # Program did not halt within max_steps
        print(f"steps exceeded at: {ip}")
        return None

    return output


def part1(data: ParsedData) -> str:
    output = execute_program(data.program, data.register_a, data.register_b, data.register_c) or []
    output_str = ",".join(map(str,output))
    return output_str

# Returns only first out value
def execute_until_out(data, a):
    res = execute_program(data.program, a, 0, 0, return_on_out=True)
    return res[0]

def part2(data: ParsedData) -> Optional[int]:

    # For my data 4 can be created from: 11 = 0b1011. So its not a 3bit, and it will overlap with the
    # next digit 3bit A sequence. So you need a dynamic programming aproach where solution is being build
    # from smaller overlapping problems. You cant solve it by analyzing each digit in separation from other
    # digits
    #for a in range(12):
    #    print(f"{a} {bin(a)} -> {execute_until_out(data, a)}")

    # Recursively build A value starting from the known output. The A value is build from the right side
    # each 3 bits represents one digit in output - but for 4 (in case of my data) the there are 4 bits, so
    # those bits overlap.
    program_len = len(data.program)
    def find_min_a_value(pos_from_right: int, current_a_to_check: int) -> int:
        if pos_from_right > program_len:
            # Whole A was filled so check if its correct
            if execute_program(data.program, current_a_to_check, data.register_b, data.register_c) == data.program:
                return current_a_to_check
            return sys.maxsize
        # Check next possible 3 bit A chunk (from the right)
        best_value = sys.maxsize
        for a in range(8):
            next_val = (current_a_to_check << 3) | a
            if execute_until_out(data, next_val) == data.program[-pos_from_right]:
                res = find_min_a_value(pos_from_right + 1, next_val)
                if res < best_value:
                    best_value = res
        return best_value
    return find_min_a_value(1, 0)

def solve(data: str, part: int = 1):
    parsed_data = parse_input(data)
    if part == 1:
        return part1(parsed_data)
    elif part == 2:
        result = part2(parsed_data)
        if result is not None:
            return result
        else:
            raise ValueError("No solution found within search limit.")


def test(part) -> bool:
    test_input_part1 = """
Register A: 729
Register B: 0
Register C: 0
Program: 0,1,5,4,3,0
"""


    """
    adv 3
    out 4
    jnz 0
"""
    test_input_part2 = """
Register A: 2024
Register B: 0
Register C: 0
Program: 0,3,5,4,3,0
"""

    all_pass = True

    if part == 1:
        all_pass = verify_result(part1(parse_input(test_input_part1)), "4,6,3,5,6,3,5,2,1,0", part)
    elif part == 2:
        all_pass = verify_result(part2(parse_input(test_input_part2)), 117440, part)

    return all_pass


if __name__ == "__main__":
    run_tests(17)
    run_day(17, part1=True, part2=True)
