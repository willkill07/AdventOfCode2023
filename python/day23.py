from collections import defaultdict


def make_graph(
    data: list[str], *, part2: bool = False
) -> defaultdict[tuple[int, int], set[tuple[int, int, int]]]:
    adj: defaultdict[tuple[int, int], set[tuple[int, int, int]]] = defaultdict(set)
    for r, row in enumerate(data):
        for c, v in enumerate(row):
            if not part2:
                match v:
                    case ".":
                        for dr, dc in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
                            if (
                                (0 <= (ar := r + dr) < len(data))
                                and (0 <= (ac := c + dc) < len(row))
                                and data[ar][ac] == "."
                            ):
                                adj[(r, c)].add((ar, ac, 1))
                                adj[(ar, ac)].add((r, c, 1))
                    case ">":
                        adj[(r, c)].add((r, c + 1, 1))
                        adj[(r, c - 1)].add((r, c, 1))
                    case "v":
                        adj[(r, c)].add((r + 1, c, 1))
                        adj[(r - 1, c)].add((r, c, 1))
            elif v in ".>v":
                for dr, dc in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
                    if (0 <= (ar := r + dr) < len(data)) and (
                        0 <= (ac := c + dc) < len(row)
                    ):
                        if data[ar][ac] in ".>v":
                            adj[(r, c)].add((ar, ac, 1))
                            adj[(ar, ac)].add((r, c, 1))
    if part2:
        while True:
            for n, e in adj.items():
                if len(e) == 2:
                    a, b = e
                    nx, ny = n
                    ax, ay, al = a
                    bx, by, bl = b
                    adj[(ax, ay)].remove((nx, ny, al))
                    adj[(bx, by)].remove((nx, ny, bl))
                    adj[(ax, ay)].add((bx, by, al + bl))
                    adj[(bx, by)].add((ax, ay, al + bl))
                    del adj[n]
                    break
            else:
                break
    return adj


def solve(
    graph: defaultdict[tuple[int, int], set[tuple[int, int, int]]],
    goal: tuple[int, int],
) -> int:
    q: list[tuple[int, int, int]] = [(0, 1, 0)]
    visited: set[tuple[int, int]] = set()
    longest: int = 0
    while q:
        match q.pop():
            case r, c, -1:
                visited.remove((r, c))
            case r, c, d if (r, c) == goal:
                longest = max(d, longest)
            case r, c, d if (r, c) not in visited:
                visited.add((r, c))
                q.append((r, c, -1))
                q.extend((ar, ac, d + l) for ar, ac, l in graph[(r, c)])
    return longest


with open("inputs/day23.txt") as f:
    data = list(map(str.rstrip, f.readlines()))
    goal: tuple[int, int] = len(data) - 1, len(data[0]) - 2
    print(solve(make_graph(data, part2=False), goal))
    print(solve(make_graph(data, part2=True), goal))
