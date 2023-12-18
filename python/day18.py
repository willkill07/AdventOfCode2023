from typing import Iterable


def calculate_area(steps: Iterable[tuple[int, int, int]]) -> int:
    x_loc: int = 0
    return int(
        sum(
            (
                # must add half of edge length to shoelace
                y * dist * (x_loc := x_loc + x * dist) + dist / 2
                for x, y, dist in steps
            ),
            # area starts at 1.0
            1.0,
        )
    )


DIRS: dict[str, tuple[int, int]] = {
    "R": (1, 0),
    "D": (0, 1),
    "L": (-1, 0),
    "U": (0, -1),
    "0": (1, 0),
    "1": (0, 1),
    "2": (-1, 0),
    "3": (0, -1),
}

plan: list[list[str]] = list(map(str.split, open("inputs/day18.txt")))


def parse1(data: list[str]) -> tuple[int, int, int]:
    return (*DIRS[data[0]], int(data[1]))


def parse2(data: list[str]) -> tuple[int, int, int]:
    color: str = data[2]
    return (*DIRS[color[7]], int(color[2:7], 16))


print(calculate_area(map(parse1, plan)))
print(calculate_area(map(parse2, plan)))
