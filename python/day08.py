import itertools
import math
import re


def endswith(x):
    return lambda y: y.endswith(x)


with open("inputs/day08.txt") as f:
    dirs, _, *edges = f.readlines()
    dirs = dirs.rstrip()
    edges = dict(
        map(
            lambda e: (lambda s, l, r, *rest: (s, {"L": l, "R": r}))(
                *re.split("[^A-Z]+", e)
            ),
            edges,
        )
    )


def part1(start="AAA", stop=lambda x: x == "ZZZ"):
    return next(
        i + 1
        for i, d in enumerate(itertools.cycle(dirs))
        if stop(start := edges[start][d])
    )


def part2():
    return math.lcm(
        *map(
            lambda x: part1(x, endswith("Z")),
            filter(endswith("A"), edges.keys()),
        )
    )


print(part1())
print(part2())
