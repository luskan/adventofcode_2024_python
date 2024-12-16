from typing import List, Tuple
from collections import defaultdict

from common import verify_result, run_day, run_tests
from functools import cmp_to_key

# Class
class ParsedData:
    __slots__ = ["line"]

    def __init__(self):
        self.line: str = ""

def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    result.line = data
    return result

def part1(data: ParsedData) -> int:
    return solver(data, 1)

def solver(data: ParsedData, part: int) -> int:
    fs: List[int] = []

    # Build the initial list
    for index, char in enumerate(data.line.strip()):
        if index % 2 == 0:
            for k in range(0, int(char)):
                fs.append(index // 2)
        else:
            for k in range(0, int(char)):
                fs.append(-1)

    if part == 1:
        last_free_index = 0
        for i in range(len(fs)-1, 0, -1):
            if fs[i] == -1:
                continue
            for k in range(last_free_index, i):
                if fs[k] == -1:
                    fs[k] = fs[i]
                    fs[i] = -1
                    last_free_index = k
                    break
            if last_free_index >= i:
                break
    else:
        # Build indexed data structures for free spaces (from left) and used blocks (from right)
        fs_len = len(fs)
        free_blocks: List[Tuple[int, int, int]] = []      # (start, end, len)
        used_blocks: List[Tuple[int, int, int, int]] = []  # (start, end, value, len)

        i = 0
        while i < fs_len:
            if fs[i] == -1:
                start = i
                while i < fs_len and fs[i] == -1:
                    i += 1
                end = i - 1
                free_blocks.append((start, end, end - start + 1))

                #It would seem to be good idea to keep free blocks count in some map to quicly know
                #how many are still available, but in case of the problem it is not needed as there is
                #plenty of free space and this check would always pass.
            else:
                i += 1

        # Identify used blocks from right side
        i = fs_len - 1
        while i >= 0:
            if fs[i] != -1:
                v = fs[i]
                end = i
                start = i
                i -= 1
                while i >= 0 and fs[i] == v:
                    start = i
                    i -= 1
                used_blocks.append((start, end, v, end - start + 1))
            else:
                i -= 1

        # used_blocks is currently from right to left, we want to process them in that order
        # so no reversion needed since we started from the right.
        # We'll try to move each used block into a suitable free block (starting from left most free block)
        # We'll iterate until no moves are possible or used_blocks are done.

        ub_idx = 0
        used_blocks_len = len(used_blocks)
        free_blocks_len = len(free_blocks)
        while ub_idx < used_blocks_len:
            ustart, uend, uv, ulen = used_blocks[ub_idx]

            # Find a free block that can accommodate this used block
            found_block = False
            fb_idx = 0
            while fb_idx < free_blocks_len:
                fstart, fend, flen = free_blocks[fb_idx]
                if flen >= ulen:
                    # Move block ustart->uend into fstart->fstart+ulen-1
                    for offset in range(ulen):
                        fs[fstart + offset] = uv
                        fs[ustart + offset] = -1

                    if flen == ulen:
                        # Update free block, it got fully filled
                        del free_blocks[fb_idx]
                        free_blocks_len -= 1
                    else:
                        # Update free block, it just got partially filled
                        free_blocks[fb_idx] = (fstart + ulen, fend, fend - fstart - ulen + 1)

                    # The used block was fully moved, move to next one.
                    ub_idx+=1
                    found_block = True
                    break
                else:
                    fb_idx += 1

            if not found_block:
                # No suitable free block found for this used block
                # Move on to the next used block
                ub_idx += 1

            #from free blocks, remove (starting from right) blocks which does not pass: fstart < ustart:
            #This gives large optimization
            while free_blocks_len > 0:
                if free_blocks[free_blocks_len - 1][0] >= ustart:
                    free_blocks_len -= 1
                else:
                    break

            if used_blocks_len == ub_idx:
                break

    # Compute check_sum
    check_sum = 0
    for i, val in enumerate(fs):
        if val == -1:
            continue
        check_sum += val * i

    return check_sum


def part2(data: ParsedData) -> int:
    return solver(data, 2)

def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)

def test(part) -> bool:
    test_input = """
2333133121414131402
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    # Test part 1
    if (part == 1):
        all_pass = all_pass and verify_result(part1(parsed_data), 1928, 1)

    # Test part 2
    if (part == 2):
        all_pass = all_pass and verify_result(part2(parsed_data), 2858, 2)

    return all_pass

if __name__ == "__main__":
    #run_tests(9)
    run_day(9, part1=True, part2=True)
