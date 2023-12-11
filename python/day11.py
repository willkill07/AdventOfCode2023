with open("inputs/day11.txt") as f:
    f = list(map(str.rstrip, f.readlines()))
    empty_rows: list[int] = list(i for i, r in enumerate(f) if all(c == "." for c in r))
    empty_cols: list[int] = list(
        j for j in range(len(f[0])) if all(r[j] == "." for r in f)
    )
    galaxies: list[tuple[int, int]] = list(
        (i, j) for i, r in enumerate(f) for j, c in enumerate(r) if c == "#"
    )


def move(g: tuple[int, int], scale: int) -> tuple[int, int]:
    def shift(pos: int, lst: list[int]) -> int:
        return pos + (scale - 1) * sum(1 for i in lst if pos >= i)

    return shift(g[0], empty_rows), shift(g[1], empty_cols)


def dist(a: tuple[int, int], b: tuple[int, int]) -> int:
    return sum((lambda a, b: abs(b - a))(*x) for x in zip(a, b))


def solve(g: list[tuple[int, int]], scale: int) -> int:
    g: list[tuple[int, int]] = list(map(lambda x: move(x, scale), g))
    return sum(dist(g1, g2) for i, g1 in enumerate(g) for g2 in g[i + 1 :])


print(solve(galaxies, 2))
print(solve(galaxies, 1000000))
