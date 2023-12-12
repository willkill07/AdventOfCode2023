import functools


@functools.cache
def solve(s: str, counts: tuple[int, ...], curr_size: int = 0):
    return (
        sum(
            # increase curr_size
            solve(s[1:], counts, curr_size + 1)
            if c == "#"
            else (
                # skip to next count if curr_size met
                (solve(s[1:], counts[1:]) if counts and counts[0] == curr_size else 0)
                if curr_size
                # don't mark the current character and start a new (potential) group
                else solve(s[1:], counts)
            )
            for c in ([".", "#"] if s[0] == "?" else s[0])
        )
        if s
        else not (counts or curr_size)
    )


with open("inputs/day12.txt") as f:
    rows = list(
        (pattern, tuple(map(int, counts.split(","))))
        for pattern, counts in map(str.split, map(str.rstrip, f.readlines()))
    )


def unfold(row: tuple[str, tuple[int, ...]]) -> tuple[str, tuple[int, ...]]:
    return "?".join(row[0] for _ in range(5)), row[1] * 5


# Part 1
print(sum(solve(group + ".", counts) for group, counts in rows))

# Part 2
print(sum(solve(group + ".", counts) for group, counts in map(unfold, rows)))
