import math
import random


def parse(filename: str) -> tuple[set[str], list[tuple[str, str]]]:
    with open(filename) as f:
        V: set[str] = set()
        E: list[tuple[str, str]] = list()
        for line in f.readlines():
            v, *ws = line.replace(":", " ").split()
            V.add(v)
            V.update(ws)
            E.extend((v, w) for w in ws)
        return V, E


def solve(V: set[str], E: list[tuple[str, str]]) -> int:
    while True:
        subsets: list[set[str]] = list({v} for v in V)
        subset = lambda v: next(s for s in subsets if v in s)
        while len(subsets) > 2:
            a, b = map(subset, random.choice(E))
            if a != b:
                a.update(b)
                subsets.remove(b)
        if sum(subset(u) != subset(v) for u, v in E) < 4:
            return math.prod(map(len, subsets))


print(solve(*parse("inputs/day25.txt")))
