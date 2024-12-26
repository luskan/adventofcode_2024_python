from typing import List, Tuple, Set
from collections import defaultdict
from itertools import combinations

from common import verify_result, run_tests, run_day


class ParsedData:
    __slots__ = ["connections"]

    def __init__(self):
        self.connections: List[Tuple[str, str]] = []


def parse_input(data: str) -> ParsedData:
    result: ParsedData = ParsedData()
    result.connections = [tuple(line.strip().split('-')) for line in data.strip().split('\n') if line.strip()]
    return result


def part1(data: ParsedData) -> int:
    networks = build_graph(data.connections)
    triangles = count_triangles(networks)
    # Filter triangles with at least one computer starting with 't'
    count = 0
    for triangle in triangles:
        if any(node.startswith('t') for node in triangle):
            count += 1
    return count


def part2(data: ParsedData) -> str:
    networks = build_graph(data.connections)
    max_clique = find_max_clique(networks)
    # Sort alphabetically and join with commas
    password = ','.join(sorted(max_clique))
    return password


def build_graph(connections: List[Tuple[str, str]]) -> defaultdict:
    networks = defaultdict(set)
    for a, b in connections:
        networks[a].add(b)
        networks[b].add(a)
    return networks


def count_triangles(networks: defaultdict) -> List[Tuple[str, str, str]]:
    """
    Count the number of triangles in the network.
    :param networks: adjacency list of the network
    :return:
    """

    triangles = []
    # Iterate over each node
    nodes = sorted(networks.keys())
    for i, a in enumerate(nodes):
        neighbors_a = networks[a]
        for b in neighbors_a:
            if b <= a:
                continue  # Ensure each pair is considered once
            neighbors_b = networks[b]
            common = neighbors_a & neighbors_b
            for c in common:
                if c > b:
                    triangles.append((a, b, c))
    return triangles


def find_max_clique(networks: defaultdict) -> Set[str]:
    # Implement Bron–Kerbosch algorithm with pivot

    # Straight implementation from: https://en.wikipedia.org/wiki/Bron%E2%80%93Kerbosch_algorithm
    def bron_kerbosch(R: Set[str], P: Set[str], X: Set[str], cliques: List[Set[str]]):

        # if P and X are both empty then
        #  report R as a maximal clique
        if not P and not X:
            cliques.append(R)
            return

        # choose a pivot vertex u in P ⋃ X
        u = next(iter(P | X))

        # for each vertex v in P \ N(u) do
        for v in P - networks[u]:
            # BronKerbosch2(R ⋃ {v}, P ⋂ N(v), X ⋂ N(v))
            bron_kerbosch(R | {v}, P & networks[v], X & networks[v], cliques)
            # P := P \ {v}
            P.remove(v)
            # X := X ⋃ {v}
            X.add(v)

    cliques = []
    P = set(networks.keys())
    bron_kerbosch(set(), P, set(), cliques)

    # Find the largest clique
    max_size = 0
    max_clique = set()
    for clique in cliques:
        if len(clique) > max_size:
            max_size = len(clique)
            max_clique = clique
    return max_clique


def solve(data: str, part: int = 1) -> int:
    parsed_data = parse_input(data)
    return part1(parsed_data) if part == 1 else part2(parsed_data)


def test(part) -> bool:
    test_input = """
kh-tc
qp-kh
de-cg
ka-co
yn-aq
qp-ub
cg-tb
vc-aq
tb-ka
wh-tc
yn-cg
kh-ub
ta-co
de-co
tc-td
tb-wq
wh-td
ta-ka
td-qp
aq-cg
wq-ub
ub-vc
de-ta
wq-aq
wq-vc
wh-yn
ka-de
kh-ta
co-tc
wh-qp
tb-vc
td-yn    
"""

    parsed_data = parse_input(test_input)

    all_pass = True

    if part == 1:
        all_pass = all_pass and verify_result(part1(parsed_data), 7, 1)

    if part == 2:
        all_pass = all_pass and verify_result(part2(parsed_data), "co,de,ka,ta", 2)

    return all_pass


if __name__ == "__main__":
    run_tests(23)
    run_day(23, part1=True, part2=True)
