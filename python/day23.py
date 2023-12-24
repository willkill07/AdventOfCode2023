from collections import defaultdict

Point = tuple[int, int]


def make_graph(
    data: list[str], *, part2: bool = False
) -> defaultdict[Point, set[tuple[Point, int]]]:
    adj: defaultdict[Point, set[tuple[Point, int]]] = defaultdict(set)
    for r, row in enumerate(data):
        for c, v in enumerate(row):
            loc: Point = (r, c)
            if not part2:
                match v:
                    case ".":
                        for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                            if (
                                (0 <= (ar := r + dr) < len(data))
                                and (0 <= (ac := c + dc) < len(row))
                                and data[ar][ac] == "."
                            ):
                                new_loc: Point = (ar, ac)
                                adj[loc].add((new_loc, 1))
                                adj[new_loc].add((loc, 1))
                    case ">":
                        adj[loc].add(((r, c + 1), 1))
                        adj[(r, c - 1)].add((loc, 1))
                    case "v":
                        adj[loc].add(((r + 1, c), 1))
                        adj[(r - 1, c)].add((loc, 1))
            elif v != "#":
                for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                    if (0 <= (ar := r + dr) < len(data)) and (
                        0 <= (ac := c + dc) < len(row)
                    ):
                        new_loc = (ar, ac)
                        if data[ar][ac] != "#":
                            adj[loc].add((new_loc, 1))
                            adj[new_loc].add((loc, 1))
    if part2:
        while True:
            for n, e in adj.items():
                if len(e) == 2:
                    (aloc, al), (bloc, bl) = e
                    adj[aloc].remove((n, al))
                    adj[bloc].remove((n, bl))
                    adj[aloc].add((bloc, al + bl))
                    adj[bloc].add((aloc, al + bl))
                    del adj[n]
                    break
            else:
                break
    return adj


def solve(
    graph: defaultdict[Point, set[tuple[Point, int]]],
    start: Point,
    goal: Point,
) -> int:
    q: list[tuple[Point, int]] = [(start, 0)]
    visited: defaultdict[Point, bool] = defaultdict(bool)
    longest: int = 0
    while q:
        loc, d = q.pop()
        if d == -1:
            visited[loc] = False
        elif loc == goal:
            longest = max(d, longest)
        elif not visited[loc]:
            visited[loc] = True
            q.append((loc, -1))
            q.extend((new_loc, d + l) for new_loc, l in graph[loc])
    return longest


with open("inputs/day23.txt") as f:
    data = list(map(str.rstrip, f.readlines()))
    start: Point = (0, 1)
    goal: Point = len(data) - 1, len(data[0]) - 2
    print(solve(make_graph(data, part2=False), start, goal))
    print(solve(make_graph(data, part2=True), start, goal))
