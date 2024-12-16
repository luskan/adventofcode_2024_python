from collections import defaultdict, deque
from common import run_tests, verify_result, run_day


class ParsedData:
    __slots__ = ["line"]

    def __init__(self):
        self.line: str = ""


def parse_input(data: str) -> ParsedData:
    result = ParsedData()
    result.line = data
    return result


def solver(data: ParsedData, part: int) -> int:
    # Split the input into a grid of characters
    grid = [list(line) for line in data.line.strip().split('\n') if line]
    if not grid:
        return 0
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    total = 0

    # For part two: Collect edges along the boundary
    FenceSet = set[tuple[int, int, int, int]] # (x1, y1, x2, y2)
    horizontal_fences: FenceSet = set()
    vertical_fences: FenceSet = set()

    # Directions: left, right, up, down
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for y in range(rows):
        for x in range(cols):
            if not visited[y][x]:
                plant_type = grid[y][x]
                # Step 1. BFS for both parts. To find all plots of this region.
                queue = deque()
                queue.append((x, y))
                visited[y][x] = True
                area = 0
                perimeter = 0

                if part == 2:
                    horizontal_fences.clear()
                    vertical_fences.clear()

                while queue:
                    current_x, current_y = queue.popleft()
                    area += 1
                    for dx, dy in directions:
                        nx, ny = current_x + dx, current_y + dy
                        if nx < 0 or nx >= cols or ny < 0 or ny >= rows or grid[ny][nx] != plant_type:
                            # This is a boundary.
                            if part == 1:
                                perimeter += 1
                            else:
                                # Step 2.
                                # Instead of just incrementing a perimeter count, store the boundary edge as a
                                # segment between two grid points ("corners").
                                #
                                # For a cell (x, y), each fence edge is stored as a pair of points.
                                # Points are always corners on the grid.
                                if dx == -1 and dy == 0:
                                    # Left edge: vertical line between (x, y) and (x, y + 1)
                                    vertical_fences.add((current_x, current_y, current_x, current_y + 1))
                                elif dx == 1 and dy == 0:
                                    # Right edge: vertical line between (x + 1, y) and (x + 1, y + 1)
                                    vertical_fences.add((current_x + 1, current_y, current_x + 1, current_y + 1))
                                elif dx == 0 and dy == -1:
                                    # Up edge: horizontal line between (x, y) and (x + 1, y)
                                    horizontal_fences.add((current_x, current_y, current_x + 1, current_y))
                                elif dx == 0 and dy == 1:
                                    # Down edge: horizontal line between (x, y + 1) and (x + 1, y + 1)
                                    horizontal_fences.add((current_x, current_y + 1, current_x + 1, current_y + 1))
                        else:
                            if not visited[ny][nx]:
                                visited[ny][nx] = True
                                queue.append((nx, ny))

                if part == 1:
                    total += area * perimeter
                else:
                    # Step 3: Building a Graph of Corner Nodes. Reconstruct the polygon(s) and count sides.
                    #
                    # We have a set of edges, each connecting two corner nodes. Think of the corner nodes as vertices in
                    # a graph, and each boundary fence edge as an undirected edge in that graph. For a better visualization,
                    # if your grid has R rows and C columns of cells, you can visualize corner nodes like a grid of dots
                    # that mark the corners. The number of such "corner nodes" is (R+1) by (C+1):
                    #
                    #    c=0    c=1    c=2 ...      c=C
                    # r=0   • ----- • ----- • ...  ----- •
                    #       |       |       |            |
                    # r=1   • ----- • ----- • ...  ----- •
                    #       |       |       |            |
                    # r=2   • ----- • ----- • ...  ----- •
                    #  ...         ...
                    # r=R   • ----- • ----- • ...  ----- •
                    #
                    #
                    # Now, construct a graph (for each region) where:
                    # Keys are corner nodes (tuples like (column, row) for a corner).
                    # Values are sets of neighboring corners connected by a fence edge.
                    Vertex2 = tuple[int, int]
                    GraphKey = Vertex2      # column, row
                    GraphValue = Vertex2    # column, row
                    edges: set[tuple[GraphKey, GraphValue]] = set()

                    def add_edge(x1, y1, x2, y2):
                        p1 = (x1, y1)
                        p2 = (x2, y2)
                        if p2 < p1:          # normalize order, to avoid duplicates
                            p1, p2 = p2, p1
                        edges.add((p1, p2))

                    for (x1, y1, x2, y2) in horizontal_fences:
                        add_edge(x1, y1, x2, y2)
                    for (x1, y1, x2, y2) in vertical_fences:
                        add_edge(x1, y1, x2, y2)

                    if not edges:
                        # No boundary - should not happen if here ?
                        assert False, "No boundary edges found"

                    # Build a graph: node -> neighbors
                    graph: defaultdict[Vertex2, set[Vertex2]] = defaultdict(set)
                    for e in edges:
                        a, b = e
                        graph[a].add(b)
                        graph[b].add(a)

                    # Find connected components of this graph
                    visited_nodes: set[Vertex2] = set()

                    def get_component(start: Vertex2) -> set[Vertex2]:
                        comp: set[Vertex2] = set()
                        stack = [start]
                        while stack:
                            u = stack.pop()
                            if u not in visited_nodes:
                                visited_nodes.add(u)
                                comp.add(u)
                                for v in graph[u]:
                                    if v not in visited_nodes:
                                        stack.append(v)
                        return comp

                    # We might have multiple connected components (holes + outer boundary)
                    # Each component may contain intersections (degree>2 nodes).
                    # Each component can form one or more loops if intersections exist.
                    # We must extract loops by a polygon tracing method.

                    def direction(a: Vertex2, b: Vertex2) -> str:
                        # a=(x1,y1), b=(x2,y2)
                        if a[0] == b[0]:
                            return 'V'
                        return 'H'

                    # Step 4: Finding Loops (Polygon Boundaries)
                    #
                    # The boundary of a polygon is a closed loop in this graph: start at some corner node and follow
                    # connecting edges until you return to the start. Each connected component of the graph forms one or
                    # more closed loops. These loops correspond to:
                    # - The outer boundary of the region, and/or
                    # - The boundaries of holes inside the region.
                    # To find these loops:
                    # 1. Identify connected components of the node graph. Each component should form at least one closed loop.
                    # 2. From each component, pick a starting node and try to walk along the edges to trace out a closed loop.
                    #    - Since these polygons are rectilinear (edges only horizontal or vertical), you try to walk
                    #      around keeping the interior on one side (e.g., always turning in a consistent manner,
                    #      or just picking edges in a systematic way that ensures you outline the polygon boundary).

                    # So to reiterate the strategy is to:
                    # 1. Pick the lowest-leftmost node in the component to start.
                    # 2. From that node, choose an initial direction by picking the neighbor that leads us forward
                    #    in a way that the interior is to our left (imagine you're walking along the edges of a fenced garden plot.
                    #    If you always keep the garden (the interior) on your left, then you will always move counterclockwise).
                    # 3. At each node, pick the next edge that turns as little as possible to the left to stay inside.
                    #
                    # Since the region is enclosed, walking the boundary in a consistent "left-hand" manner
                    # will trace one closed loop. Remove used edges from a temporary copy until no edges left.

                    # To implement "left-hand rule" simply for orthogonal polygons:
                    # Directions: up(0,-1), down(0,1), left(-1,0), right(1,0)
                    # We'll represent directions as vectors and always turn left if possible.
                    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # clockwise order: up, right, down, left

                    # left turn: index - 1 mod 4, right turn: index + 1 mod 4
                    # We'll find the current direction index and choose next direction by preferring left turns.

                    def dir_index(d: Vertex2) -> int:
                        return dirs.index(d)

                    def vector(a: Vertex2, b: Vertex2) -> Vertex2:
                        return b[0] - a[0], b[1] - a[1]

                    # If we want inside on the left, we should choose edges in an order that turns left first.
                    # left(3) is best, then straight(0), then right(1), then back(2)
                    def choose_direction(curr_dir: Vertex2, candidate_dirs: list[Vertex2]) -> Vertex2:
                        # candidate_dirs is a list of possible next directions
                        # Evaluate turn_direction and pick the one with minimal "cost" according to left turn priority
                        # left(3) best -> assign a priority: {3:1,0:2,1:3,2:4} smaller is better
                        priority_map = {3: 1, 0: 2, 1: 3, 2: 4}
                        best = None
                        best_p = 5
                        for nd in candidate_dirs:
                            diff = (dir_index(nd) - dir_index(curr_dir)) % 4
                            p = priority_map.get(diff, 5)
                            if p < best_p:
                                best_p = p
                                best = nd
                        return best

                    def trace_loops(comp_nodes: set[Vertex2]) -> list[list[Vertex2]]:
                        # We will work on a copy of edges
                        local_graph: dict[Vertex2, set[Vertex2]] = {n: set(g) for n, g in graph.items() if n in comp_nodes}
                        all_loops: list[list[Vertex2]] = []

                        # Convert sets of neighbors to a mutable structure

                        # Find a starting node: lowest-leftmost
                        # There might be multiple loops due to intersections
                        # We'll find loops until no edges remain
                        all_edges_in_comp: set[tuple[Vertex2, Vertex2]] = set()
                        for u in local_graph:
                            for v in local_graph[u]:
                                if u < v:
                                    all_edges_in_comp.add((u, v))
                                else:
                                    all_edges_in_comp.add((v, u))

                        used_edges: set[tuple[Vertex2, Vertex2]] = set()

                        while all_edges_in_comp:
                            start = min(comp_nodes)  # lowest-leftmost node
                            # Ensure start has edges
                            # If start isolated (no edges), remove it
                            if not local_graph[start]:
                                comp_nodes.remove(start)
                                continue

                            # Pick a neighbor of start to begin
                            first_n = min(local_graph[start])
                            loop = [start, first_n]
                            # Determine initial direction
                            curr_dir = vector(start, first_n)

                            # Mark edge as used
                            used_edges: set[tuple[Vertex2, Vertex2]] = set()

                            def use_edge(a: Vertex2, b: Vertex2) -> None:
                                e: tuple[Vertex2, Vertex2] = (a, b) if a < b else (b, a)
                                used_edges.add(e)

                            use_edge(start, first_n)

                            curr = first_n
                            prev = start

                            while True:
                                # possible next steps are neighbors of curr except prev?
                                nbrs = [w for w in local_graph[curr] if w != prev]
                                if not nbrs:
                                    # dead end - not a proper loop
                                    break
                                # Determine directions of candidate moves
                                candidate_moves = []
                                for w in nbrs:
                                    d = vector(curr, w)
                                    candidate_moves.append(d)
                                # choose direction with left-hand rule
                                next_dir = choose_direction(curr_dir, candidate_moves)
                                if next_dir is None:
                                    break  # No valid direction
                                # find which w matches next_dir
                                next_node = None
                                for w in nbrs:
                                    if vector(curr, w) == next_dir:
                                        next_node = w
                                        break
                                if next_node is None:
                                    break
                                loop.append(next_node)
                                use_edge(curr, next_node)

                                prev, curr_dir, curr = curr, next_dir, next_node
                                if curr == start:
                                    # closed loop
                                    break

                            # Remove used edges from all_edges_in_comp
                            all_edges_in_comp = {e for e in all_edges_in_comp if e not in used_edges}
                            # Also remove them from local_graph
                            for (a, b) in used_edges:
                                if b in local_graph[a]:
                                    local_graph[a].remove(b)
                                if a in local_graph[b]:
                                    local_graph[b].remove(a)

                            if len(loop) > 2 and loop[-1] == loop[0]:
                                all_loops.append(loop)

                            # Remove isolated nodes if any
                            isolated = [n for n in comp_nodes if not local_graph[n]]
                            for iso in isolated:
                                comp_nodes.remove(iso)
                                del local_graph[iso]

                        return all_loops

                    sides_count = 0
                    comp_nodes_list = []

                    # Get components
                    all_nodes = list(graph.keys())
                    visited_nodes.clear()
                    for node in all_nodes:
                        if node not in visited_nodes:
                            comp = get_component(node)
                            if comp:
                                comp_nodes_list.append(comp)

                    # Trace loops for each component and sum sides
                    for comp_nodes in comp_nodes_list:

                        # Step 5: Reconstructing the Polygon’s Edges in Order
                        # During iteration from one node to another, nodes are recorded as a sequence.
                        # By doing so, we get a loop: a list of nodes [N0, N1, N2, ..., N0].
                        # Each pair (N0,N1), (N1,N2), ... is an edge of the polygon boundary in order.
                        loops = trace_loops(set(comp_nodes))

                        # Step 6: Counting Sides
                        #
                        # Once you have loop, we determine the "direction" of each edge:
                        #
                        # Horizontal edges (where x is constant but y changes) are "H".
                        # Vertical edges (where y is constant but x changes) are "V".
                        # As you go around the loop in order, you record these directions. For example, you might get a
                        # direction list like: H, H, V, V, V, H, H, ...
                        #
                        # Defining a Side: A side is a maximal consecutive run of edges with the same direction.
                        # For example:
                        #
                        # If the direction sequence is H, H, V, V, H, H, H, V, the sides are:
                        # - Two horizontal edges in a row count as one "horizontal side".
                        # - Then two vertical edges as one "vertical side".
                        # - Then three horizontal edges as one "horizontal side".
                        # - Then one vertical edge as one "vertical side".
                        # and finally - this results in 4 sides for that loop.
                        # If your region has multiple loops (one outer boundary and possibly several inner boundaries),
                        # you do this sides counting for each loop and sum them up.
                        for loop in loops:
                            # loop is a sequence of nodes, last=first
                            # get edges and directions
                            loop_edges = list(zip(loop, loop[1:]))
                            # directions_list
                            directions_list = [direction(a, b) for (a, b) in loop_edges]
                            # merge consecutive same directions into one side:
                            sides = 1
                            for i in range(1, len(directions_list)):
                                if directions_list[i] != directions_list[i - 1]:
                                    sides += 1
                            sides_count += sides

                    total += area * sides_count

    return total


def part1(data: ParsedData) -> int:
    return solver(data, 1)


def part2(data: ParsedData) -> int:
    return solver(data, 2)


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test(part) -> bool:
    test_cases = [
        {
            'input': """
AAAA
BBCD
BBCC
EEEC
""",
            'expected_part1': 140,
            'expected_part2': 80
        },
        {
            'input': """
OOOOO
OXOXO
OOOOO
OXOXO
OOOOO
""",
            'expected_part1': 772,
            'expected_part2': 436
        },
        {
            'input': """
EEEEE
EXXXX
EEEEE
EXXXX
EEEEE
""",
            'expected_part1': -1,  # only in part2
            'expected_part2': 236
        },
        {
            'input': """
AAAAAA
AAABBA
AAABBA
ABBAAA
ABBAAA
AAAAAA
""",
            'expected_part1': -1,
            'expected_part2': 368
        },
        {
            'input': """
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
""",
            'expected_part1': 1930,
            'expected_part2': 1206
        }
    ]

    all_pass = True

    for idx, case in enumerate(test_cases, 1):
        parsed_data = parse_input(case['input'])

        if part == 1:
            expected = case['expected_part1']
            if expected == -1:
                continue
            result = part1(parsed_data)
        else:
            expected = case['expected_part2']
            if expected == -1:
                continue
            result = part2(parsed_data)

        if not verify_result(result, expected, part):
            print(f"Test case {idx} failed for part {part}: got {result}, expected {expected}")
            all_pass = False
        else:
            print(f"Test case {idx} passed for part {part}.")

    return all_pass


if __name__ == "__main__":
    run_tests(12)
    run_day(12, part1=True, part2=True)
