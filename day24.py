from typing import List, Tuple, Set
from collections import deque, defaultdict
from common import verify_result, run_day, run_tests

"""
Schematic of a RCA from the problem.

4-bit adder (RCA - Ripple Carry Adder) with inputs x0,x1,x2,x3 (first number) and y0,y1,y2,y3 (second number).
Below is a correct layout how it should look like. Later code will try to verify if outputs are correctly
connected to inputs. 

x0 XOR y0 -> t1   (first XOR for sum)      - t1=output_name_1st_xor
x0 AND y0 -> c0   (generates carry)        - c0=output_name_carry_out
-                                          - None=output_name_carry_propagate
-                                          - None=output_name_partial_carry
t1 XOR c0 -> s0   (final sum for bit 0)    - s0=output_name_sum

For bit position 1:
4. x1 XOR y1 -> t2   (first XOR for sum)   - t2=output_name_1st_xor
5. x1 AND y1 -> t3   (partial carry)       - t3=output_name_partial_carry
6. c0 AND t2 -> t4   (carry propagate)     - t4=output_name_carry_propagate
7. t3 OR t4 -> c1    (carry out for bit 1) - c1=output_name_carry_out
8. t2 XOR c0 -> s1   (final sum for bit 1) - s1=output_name_sum
For bit position 2:
9. x2 XOR y2 -> t5   (first XOR for sum)  - t5=output_name_1st_xor
10. x2 AND y2 -> t6  (partial carry)      - t6=output_name_partial_carry
11. c1 AND t5 -> t7  (carry propagate)    - t7=output_name_carry_propagate
12. t6 OR t7 -> c2   (carry out for bit 2)- c2=output_name_carry_out
13. t5 XOR c1 -> s2  (final sum for bit 2)- s2=output_name_sum
For bit position 3:
14. x3 XOR y3 -> t8  (first XOR for sum)   - t8=output_name_1st_xor
15. x3 AND y3 -> t9  (partial carry)       - t9=output_name_partial_carry
16. c2 AND t8 -> t10 (carry propagate)     - t10=output_name_carry_propagate
17. t9 OR t10 -> c3  (final carry out)     - c3=output_name_carry_out
18. t8 XOR c2 -> s3  (final sum for bit 3)- s3=output_name_sum
"""

# Order 0-3 is the same as in RCP (Ripple Carry Adder) diagram, excluding the first two gates which are easily being found
# due to the inputs being x0 and y0s.
GATE_AND = 0
GATE_OR = 1
GATE_XOR = 2
GATE_NOTE = 3 # Not a gate, contains some msg as tuple element 1

LogicGate = Tuple[str, int, str, str]
LogicGateGroup = List[LogicGate]

class ParsedData:
    __slots__ = ["wires", "gates"]

    def __init__(self):
        self.wires: dict[str, int] = {}
        self.gates: LogicGateGroup = []

def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    lines = data.strip().split('\n')
    for line in lines:
        parts = line.split(' ')
        if len(parts) == 2:
            result.wires[parts[0][:-1]] = int(parts[1])
        elif len(parts) == 5:
            #ntg XOR fgs -> mjb
            gate = (parts[0],
                 GATE_AND if parts[1] == 'AND'
                 else GATE_OR if parts[1] == 'OR'
                 else GATE_XOR,
                 parts[2],
                 parts[4])

            # Do some initial ordering, x should always be on the left side, also sort output names
            ch1 = gate[0][0]
            ch2 = gate[2][0]
            if (ch1 == 'y' and ch2 == 'x') or \
               (ch2 == 'y' and ch1 != 'x') or \
               (ch2 == 'x' and ch1 != 'y') or \
               (gate[0] < gate[2] and ch1 not in 'xy' and ch2 not in 'xy'):
                # Make sure x is always on the left side
                gate = (gate[2], gate[1], gate[0], gate[3])
            result.gates.append(gate)
    return result

def gate_name(gate_type: int):
    if gate_type == GATE_AND:
        return "AND"
    elif gate_type == GATE_OR:
        return "OR"
    elif gate_type == GATE_XOR:
        return "XOR"
    else:
        return "UNKNOWN"

# Nicely print the logic gate
def gate_map(gate: LogicGate) -> str:
    return f"{gate[0]} {gate_name(gate[1])} {gate[2]} -> {gate[3]}"

def write_reordered_data(data: ParsedData):
    """
    !!! This is my first approach, ugly and requires manual work to find the error. find_switched_outputs does
    it automatically.

    Write the reordered data to the console. Does not fix the output, but writes it nicely and
    informs where the error is located. Further deduction must be done manually. For auto deduction use
    find_switched_outputs function.

    If it finds an error in logic group for example #12, then it will probably also print error for #13, as
    messed outputs from #12 causes logic errors in #13. At #14 all shold be back correct again.
    """

    print("\n\nReordered data with error hints:")

    # Count number of x and y input bits
    x_bits = sum(1 for w in data.wires if w.startswith('x'))

    prev_output_name_carry_out = "?"
    output_name_carry_out = "?"

    # Gates for which correct pattern was found
    ordered_gates: LogicGateGroup = []

    # Gates for which pattern was not found, probably due to nearby error in swapped outputs
    orfaned_gates: LogicGateGroup = []

    for gate_index in range(x_bits):
        # collect all gates which contain f'x{i:02d}'
        ordered_gates.append((f"#{gate_index}", GATE_NOTE, "", ""))

        group = []

        #
        # Create a group of joined elements (a clique) which are connected to the same inputs

        in1_name = f'x{gate_index:02d}'
        in2_name = f'y{gate_index:02d}'
        for gate in data.gates:
            if f'x{gate_index:02d}' in gate or f'y{gate_index:02d}' in gate:
                group.append(gate)
                if gate_index > 0:
                    for gate2 in data.gates:
                        if gate[3] in gate2 and gate2 != gate:
                            gate2_new = gate2
                            if gate2_new[2] == gate[3]:
                                gate2_new = (gate2_new[2], gate2_new[1], gate2_new[0], gate2_new[3])
                            if gate2 in group:
                                group.remove(gate2)
                            if gate2_new not in group:
                                group.append(gate2_new)

                            for gate3 in data.gates:
                                if (gate2[3] == gate3[0] or gate2[3] == gate3[2]) and gate2[1] == GATE_AND:
                                    if gate3 not in group and gate2 != gate3 and gate3 != gate2_new and gate != gate3:
                                        if (gate3[2], gate3[1], gate3[0], gate3[3]) not in group:
                                            group.append(gate3)


        #
        # Now the ugly logic for cleaning up the input. We have te group of gates, but they are not ordered,
        # and with swapped outputs, so lots of logic.

        #Find in group tuple which for gate[0] has in1_name, and for gate[2] has in2_name, and type is XOR
        output_name_1st_xor = None
        output_name_partial_carry = None
        output_name_carry_propagate = None
        output_name_sum = None
        for gate in group:
            # x2 XOR y2 -> t5
            if gate[0] == in1_name and gate[2] == in2_name and gate[1] == GATE_XOR:
                ordered_gates.append(gate)
                group.remove(gate)
                output_name_1st_xor = gate[3]
                if gate_index == 0:
                    output_name_sum = gate[3]
                break
        for gate in group:
            # x2 AND y2 -> t6  (partial carry) - for gate index > 0
            # x0 AND y0 -> c0   (generates carry) - for gate index = 0
            if gate[0] == in1_name and gate[2] == in2_name and gate[1] == GATE_AND:
                ordered_gates.append(gate)
                group.remove(gate)
                if gate_index == 0:
                    output_name_carry_out = gate[3]
                    prev_output_name_carry_out = output_name_carry_out
                else:
                    output_name_partial_carry = gate[3]
                break
        for gate in group:
            # c0 AND t2 -> t4   (carry propagate)
            if (gate[2] == output_name_1st_xor or gate[0] == output_name_1st_xor) and gate[1] == GATE_AND:
                group.remove(gate)
                if gate[0] == output_name_1st_xor:
                    gate = (gate[2], gate[1], gate[0], gate[3])
                ordered_gates.append(gate)
                output_name_carry_propagate = gate[3]
                break
        for gate in group:
            #t3 OR t4 -> c1    (carry out for bit 1)
            if ((gate[2] == output_name_partial_carry and gate[0] == output_name_carry_propagate) or
                (gate[2] == output_name_carry_propagate and gate[0] == output_name_partial_carry)) and \
                 gate[1] == GATE_OR:
                group.remove(gate)
                if gate[2] == output_name_partial_carry:
                    gate = (gate[2], gate[1], gate[0], gate[3])
                ordered_gates.append(gate)
                prev_output_name_carry_out = output_name_carry_out
                output_name_carry_out = gate[3]
                if gate[2] != output_name_carry_propagate:
                    print(f"Error cp: {gate}")
                break
        for gate in group:
            #t1 XOR c0 -> s0   (final sum for bit 0)
            #t2 XOR c0 -> s1   (final sum for bit 1)
            if ((gate[2] == prev_output_name_carry_out and gate[0] == output_name_1st_xor) or
                    (gate[2] == output_name_1st_xor or gate[0] == prev_output_name_carry_out)) and gate[1] == GATE_XOR:
                group.remove(gate)
                if gate_index > 0:
                    if gate[2] == output_name_1st_xor:
                        gate = (gate[2], gate[1], gate[0], gate[3])
                    ordered_gates.append(gate)
                    if gate[2] != prev_output_name_carry_out:
                        print(f"Error cp: {gate}")
                    output_name_sum = gate[3]
                break

        # count elements in group which are non GATE_NOTE
        #gates_count_in_group = sum(1 for gate in group if gate[1] != GATE_NOTE)
        #assert 5 == gates_count_in_group or gate_index == 0 and gates_count_in_group == 3
        if len(group) != 0:
            orfaned_gates.extend(group)
        note = f"   {output_name_1st_xor}, {output_name_partial_carry}, {output_name_carry_propagate}, {output_name_carry_out}(prev={prev_output_name_carry_out}), {output_name_sum}"
        ordered_gates.append((note, GATE_NOTE, "", ""))
        if (len(group) != 0 or
                gate_index > 0 and None in (output_name_1st_xor, output_name_partial_carry, output_name_carry_propagate, output_name_carry_out, output_name_sum) or
                gate_index == 0 and None in (output_name_1st_xor, output_name_carry_out, output_name_sum)
            ):
            ordered_gates.append((" !ERROR", GATE_NOTE, "", ""))
        if len(group) != 0:
            # sort ordered_gates so its always in type order of GATE_AND, GATE_OR, GATE_XOR
            group.sort(key=lambda x: x[1])
            ordered_gates.append((" !Unk. groups: \n   " + "\n   ".join(map(gate_map, group)), GATE_NOTE, "", ""))
        ordered_gates.append(("\n", GATE_NOTE, "", ""))

    after_analyzis_count = 0
    gate_group_count = 0
    for gate in ordered_gates:
        if gate[1] != GATE_NOTE:
            after_analyzis_count+=1
            gate_group_count += 1
            print(f" - {gate[0]} {gate_name(gate[1])} {gate[2]} -> {gate[3]}")
        else:
            gate_group_count=0
            print(f"{gate[0]}")

    print(f"Ordered gates count: {after_analyzis_count}")
    print(f"\nOrfaned gates:")
    for gate in orfaned_gates:
        print(f" - {gate[0]} {gate_name(gate[1])} {gate[2]} -> {gate[3]}")
    print(f"Orfaned gates count: {len(orfaned_gates)}\n")

def find_switched_outputs(data: ParsedData) -> List[Tuple[str, str]]:
    wrong_outputs: List[Tuple[str, str]] = []

    # Count number of x and y input bits
    x_bits = sum(1 for w in data.wires if w.startswith('x'))

    prev_output_name_carry_out = "?"
    output_name_carry_out = "?"

    for gate_index in range(x_bits):
        group: LogicGateGroup = []

        #
        # Create a group of joined elements (a clique) which are connected to the same inputs
        for gate in data.gates:
            if f'x{gate_index:02d}' in gate or f'y{gate_index:02d}' in gate:
                group.append(gate)
                if gate_index > 0:
                    for gate2 in data.gates:
                        if gate[3] in gate2 and gate2 != gate:
                            gate2_new = gate2
                            if gate2_new[2] == gate[3]:
                                gate2_new = (gate2_new[2], gate2_new[1], gate2_new[0], gate2_new[3])
                            if gate2 in group:
                                group.remove(gate2)
                            if gate2_new not in group:
                                group.append(gate2_new)

                            for gate3 in data.gates:
                                if (gate2[3] == gate3[0] or gate2[3] == gate3[2]) and gate2[1] == GATE_AND:
                                    if gate3 not in group and gate2 != gate3 and gate3 != gate2_new and gate != gate3:
                                        if (gate3[2], gate3[1], gate3[0], gate3[3]) not in group:
                                            group.append(gate3)


        #
        # Sort elements of a group in the exact order as in the comment above

        # Helper function to move logic gates in the group to their correct indexes.
        def extract_swap(logic_group: LogicGateGroup, name: str, gate_type: int, start_index: int, dest_index: int):
            if dest_index >= len(logic_group):
                raise IndexError(f"Destination index {dest_index} is out of range for the group list.")
            index = -1
            for i, gate in enumerate(logic_group):
                if i >= start_index and (gate[0].startswith(name) or name == '') and gate[1] == gate_type:
                    index = i
                    break
            if index == -1:
                raise ValueError(
                    f"No gate found with name starting with '{name}' and gate_type '{gate_type}' starting from index {start_index}")
            logic_group[dest_index], logic_group[index] = logic_group[index], logic_group[dest_index]

        # Reorder gates to their correct indexes, as in RCP schematic.
        extract_swap(group,"x", GATE_XOR, 0, 0)
        extract_swap(group,"x", GATE_AND, 0, 1)
        if gate_index > 0:
            extract_swap(group,"", GATE_AND, 2, 2)
            extract_swap(group,"", GATE_OR, 2, 3)
            extract_swap(group,"", GATE_XOR, 2, 4)

        # Now, we now that only outputs are messed up, so having correctly ordered the group of logic units,
        # we can use their inputs to find the correct outputs (using the logic schematic from the comment at the top of file)
        #  (*) I assume that swaps are only omong the logical groups of adder, not between them

        correct_outputs: List[str]
        if gate_index == 0:
            # First group is easy to deduce, as it has only two gates, and the output is easily found from the inputs
            correct_outputs = [
                f"z{gate_index:02d}",
                group[1][3],            # Same as before (*)
            ]
            prev_output_name_carry_out = group[0][3]
        else:
            # Find the name of a new carry out, it will be used in the next logic group so in current group
            # it should not be found as an input name.
            outputs_1_to_3 = [group[1][3], group[2][3], group[3][3]]
            for test_out in outputs_1_to_3:
                wrong = False
                for gate in group:
                    if test_out == gate[0] or test_out == gate[2]:
                        wrong = True
                        break
                if not wrong:
                    output_name_carry_out = test_out
                    outputs_1_to_3.remove(output_name_carry_out)
                    break
            if output_name_carry_out is None:
                raise ValueError(f"Error: output_name_carry_out_2 not found")

            if len(outputs_1_to_3) != 2:
                raise ValueError(f"Error: outputs_1_to_3 of wrong size: {len(outputs_1_to_3)}")

            correct_outputs = [
                # To find output name for the first line (XOR), we look into the:
                # 6. c0 AND t2 -> t4   (carry propagate)
                # and choose t2, (data is very messed up) since it can be on left or right of AND, we look on both sides
                group[2][2] if group[2][0] == prev_output_name_carry_out else group[2][0],

                outputs_1_to_3[0], # Those two can be of any order actually
                outputs_1_to_3[1], # <-----/
                output_name_carry_out,
                f"z{gate_index:02d}"
            ]

        diff: List[Tuple[str, str]] = []
        correct_outputs: List[str]

        if gate_index == 0:
            # Only two outputs. We check only first, as if it does not match then the second one is also wrong.
            if group[0][3] != correct_outputs[0]:
                diff.append((group[0][3], correct_outputs[0]))
        else:
            # Only one swap per group is allowed. So lets choose first the most obvious ones.
            # Like the output bit first (z01,...).
            if group[4][3] != correct_outputs[4]:
                diff.append((group[4][3], correct_outputs[4]))
            # This one, the current logic group carry out is also quite easily to deduce, so its reliable
            elif group[3][3] != correct_outputs[3]:
                diff.append((group[3][3], correct_outputs[3]))
            # Then the output for first xor, which is quite reliable to find from the other outputs and previous carry out.
            elif group[0][3] != correct_outputs[0]:
                diff.append((group[0][3], correct_outputs[0]))
            else:
                # Now the two intermediate values: partial carry and carry propagate. Their names can be freely swapped,
                # as it does not change the output logic.
                s1 = [group[1][3], group[2][3]]
                s1.sort()
                s2 = [correct_outputs[1], correct_outputs[2]]
                s2.sort()
                if s1 != s2:
                    diff.append((s1[0], s2[0]))
                    diff.append((s1[1], s2[1]))
            wrong_outputs.extend(diff)
    return wrong_outputs

def part1(data: ParsedData) -> int:
    return solver(data)

def solver(data: ParsedData) -> int:
    queue = deque()
    for gate in data.gates:
        queue.append(gate)

    while queue:
        gate = queue.popleft()
        g1 = gate[0]
        g2 = gate[2]
        if g1 not in data.wires or g2 not in data.wires:
            queue.append(gate)
            continue
        g3 = gate[3]

        val1 = data.wires[g1]
        val2 = data.wires[g2]

        gate_type = gate[1]
        if gate_type == GATE_AND:
            data.wires[g3] = val1 & val2
        elif gate_type == GATE_OR:
            data.wires[g3] = val1 | val2
        elif gate_type == GATE_XOR:
            data.wires[g3] = val1 ^ val2
        else:
            raise ValueError(f"Unknown gate type: {gate_type}")

    # Iterate each wirte starting with z
    result = 0
    for wire in data.wires:
        if wire.startswith('z'):
            bit_number = int(wire[1:])
            value = data.wires[wire]
            result |= value << bit_number

    return result

def part2(data: ParsedData) -> str:
    swithed_outputs = find_switched_outputs(data)

    #write_reordered_data(data)

    # Prepare the output
    array_of_outputs = []
    for output in swithed_outputs:
        array_of_outputs.append(str(output[0]))
        array_of_outputs.append(str(output[1]))
    sorted_outputs = sorted(array_of_outputs)
    # remove duplicates from sorted_outputs - probably not needed
    sorted_outputs = list(dict.fromkeys(sorted_outputs))

    return ','.join(sorted_outputs)

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input1 = """
x00: 1
x01: 1
x02: 1
y00: 0
y01: 1
y02: 0

x00 AND y00 -> z00
x01 XOR y01 -> z01
x02 OR y02 -> z02
"""

    test_input2 = """
x00: 1
x01: 0
x02: 1
x03: 1
x04: 0
y00: 1
y01: 1
y02: 1
y03: 1
y04: 1

ntg XOR fgs -> mjb
y02 OR x01 -> tnw
kwq OR kpj -> z05
x00 OR x03 -> fst
tgd XOR rvg -> z01
vdt OR tnw -> bfw
bfw AND frj -> z10
ffh OR nrd -> bqk
y00 AND y03 -> djm
y03 OR y00 -> psh
bqk OR frj -> z08
tnw OR fst -> frj
gnj AND tgd -> z11
bfw XOR mjb -> z00
x03 OR x00 -> vdt
gnj AND wpb -> z02
x04 AND y00 -> kjc
djm OR pbm -> qhw
nrd AND vdt -> hwm
kjc AND fst -> rvg
y04 OR y02 -> fgs
y01 AND x02 -> pbm
ntg OR kjc -> kwq
psh XOR fgs -> tgd
qhw XOR tgd -> z09
pbm OR djm -> kpj
x03 XOR y03 -> ffh
x00 XOR y04 -> ntg
bfw OR bqk -> z06
nrd XOR fgs -> wpb
frj XOR qhw -> z04
bqk OR frj -> z07
y03 OR x01 -> nrd
hwm AND bqk -> z03
tgd XOR rvg -> z12
tnw OR pbm -> gnj
"""

    all_pass = True

    # Test part 1
    if (part == 1):
        all_pass = all_pass and verify_result(part1(parse_input(test_input1)), 4, 1)
        all_pass = all_pass and verify_result(part1(parse_input(test_input2)), 2024, 1)

    # Test part 2
    #if (part == 2):
    #    all_pass = all_pass and verify_result(part2(parsed_data), 0, 2)

    return all_pass

if __name__ == "__main__":
    run_tests(24)
    run_day(24, part1=True, part2=True)
