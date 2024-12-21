from typing import List

class ParsedData:
    __slots__ = ["register_a", "register_b", "register_c", "program"]

    def __init__(self):
        self.register_a: int = 0
        self.register_b: int = 0
        self.register_c: int = 0
        self.program: List[int] = []

OPCODE_MAPPING = {
    0: {'name': 'adv', 'operand_type': 'combo'},
    1: {'name': 'bxl', 'operand_type': 'literal'},
    2: {'name': 'bst', 'operand_type': 'combo'},
    3: {'name': 'jnz', 'operand_type': 'literal'},
    4: {'name': 'bxc', 'operand_type': 'ignored'},
    5: {'name': 'out', 'operand_type': 'combo'},
    6: {'name': 'bdv', 'operand_type': 'combo'},
    7: {'name': 'cdv', 'operand_type': 'combo'},
}

OPERAND_REGISTERS = {
    4: 'A',
    5: 'B',
    6: 'C',
}

def translate_to_python(parsed_data: ParsedData) -> str:
    program = parsed_data.program
    register_a = parsed_data.register_a
    register_b = parsed_data.register_b
    register_c = parsed_data.register_c

    code_lines = []

    # Start defining the function
    code_lines.append("def translated_program():")
    code_lines.append("\t# Initialize registers")
    code_lines.append(f"\tA = {register_a}")
    code_lines.append(f"\tB = {register_b}")
    code_lines.append(f"\tC = {register_c}\n")

    # Initialize output list
    code_lines.append("\t# Initialize output list")
    code_lines.append("\toutput = []\n")

    code_lines.append(f"\t# code: {','.join(map(str, parsed_data.program))}")

    # Start the loop
    code_lines.append("\twhile True:")

    # Process the program list in opcode-operand pairs
    for i in range(0, len(program), 2):
        opcode = program[i]
        operand = program[i + 1]

        # Get instruction details
        instr_details = OPCODE_MAPPING.get(opcode, None)
        if not instr_details:
            raise ValueError(f"Invalid opcode: {opcode}")

        instr_name = instr_details['name']
        operand_type = instr_details['operand_type']

        # Determine the operand's value based on operand_type
        if operand_type == 'literal':
            operand_value = operand
            comment_operand = f"{operand}"
        elif operand_type == 'combo':
            # Map operand to register or literal
            operand_register = OPERAND_REGISTERS.get(operand, None)
            if operand_register:
                operand_value = operand_register
                comment_operand = f"{operand_register}"
            else:
                # Operand is a literal
                operand_value = operand
                comment_operand = f"{operand}"
        elif operand_type == 'ignored':
            # Operand is read but ignored (as defined in aoc 17 problem defs.)
            operand_value = None
            comment_operand = f"{operand} (ignored)"
        else:
            operand_value = operand
            comment_operand = f"{operand}"

        # Generate the instruction translation
        op_desc = f"# {opcode},{operand} - {instr_name} {operand}"
        if instr_name == 'bst':
            # B = operand_value % 8
            if isinstance(operand_value, str):
                code_lines.append(f"\t\tB = {operand_value} % 8                 {op_desc}" )
            else:
                code_lines.append(f"\t\tB = {operand_value} % 8                 {op_desc}")
        elif instr_name == 'bxl':
            # B ^= operand_value
            code_lines.append(f"\t\tB ^= {operand_value}                    {op_desc}")
        elif instr_name == 'cdv':
            # C = A // (2 ** operand_value)
            code_lines.append(f"")
            code_lines.append(f"        {op_desc}")
            denominator = f"(2 ** {operand_value})"
            code_lines.append(f"\t\tdenominator = 2 ** {operand_value}  # {denominator}")
            code_lines.append(f"\t\tif denominator == 0:")
            code_lines.append(f"\t\t\tC = 0")
            code_lines.append(f"\t\telse:")
            code_lines.append(f"\t\t\tC = A // denominator\n")
        elif instr_name == 'bxc':
            # B ^= C
            code_lines.append(f"\t\tB ^= C                    {op_desc}")
        elif instr_name == 'adv':
            code_lines.append(f"")
            code_lines.append(f"\t\t{op_desc}")
            # A = A // (2 ** operand_value)
            denominator = f"(2 ** {operand_value})"
            code_lines.append(f"\t\tdenominator = 2 ** {operand_value}  # {denominator}")
            code_lines.append(f"\t\tif denominator == 0:")
            code_lines.append(f"\t\t\tA = 0")
            code_lines.append(f"\t\telse:")
            code_lines.append(f"\t\t\tA = A // denominator\n")
        elif instr_name == 'out':
            code_lines.append(f"\t\t{op_desc}")
            # output_value = operand_value % 8
            if operand_type == 'combo' and isinstance(operand_value, str):
                # operand_value is a register
                code_lines.append(f"\t\toutput_value = {operand_value} % 8")
            else:
                # operand_value is a literal
                code_lines.append(f"\t\toutput_value = {operand_value} % 8")
            code_lines.append(f"\t\toutput.append(str(output_value))\n")
        elif instr_name == 'jnz':
            code_lines.append(f"\t\t{op_desc}")
            # if A !=0: continue else: break
            code_lines.append(f"\t\tif A != 0:")
            code_lines.append(f"\t\t\tcontinue")
            code_lines.append(f"\t\telse:")
            code_lines.append(f"\t\t\tbreak\n")
        elif instr_name == 'bdv':
            code_lines.append(f"")
            code_lines.append(f"\t\t{op_desc}")
            # B = A // (2 ** operand_value)
            denominator = f"(2 ** {operand_value})"
            code_lines.append(f"\t\tdenominator = 2 ** {operand_value}  # {denominator}")
            code_lines.append(f"\t\tif denominator == 0:")
            code_lines.append(f"\t\t\tB = 0")
            code_lines.append(f"\t\telse:")
            code_lines.append(f"\t\t\tB = A // denominator\n")
        else:
            raise ValueError(f"unknown: {instr_name} {operand}")

    # Terminate the loop
    code_lines.append("\t# Join the output list into a comma-separated string")
    code_lines.append("\toutput_str = \",\".join(output)")
    code_lines.append("\tprint(\"Program Output:\", output_str)")
    code_lines.append("\treturn output_str\n")

    # Define the main guard
    code_lines.append("# Run the translated program")
    code_lines.append("if __name__ == \"__main__\":")
    code_lines.append("\ttranslated_program()\n")

    # Join all code lines into a single string
    translated_code = "\n".join(code_lines)

    return translated_code

# Example usage
def main():
    # Create a ParsedData instance with your input
    parsed_data = ParsedData()
    parsed_data.register_a = 30553366
    parsed_data.register_b = 0
    parsed_data.register_c = 0
    parsed_data.program = [2,4,1,1,7,5,4,7,1,4,0,3,5,5,3,0]

    # Translate the program to Python code
    translated_code = translate_to_python(parsed_data)

    # Print the translated code
    print(translated_code)

if __name__ == "__main__":
    main()
