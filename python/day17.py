import heapq
import dataclasses
from typing import Self


@dataclasses.dataclass(order=True, frozen=True)
class Point:
    y: int
    x: int

    def __add__(self, other: Self) -> Self:
        return Point(self.y + other.y, self.x + other.x)

    def __mul__(self, scale: int) -> Self:
        return Point(self.y * scale, self.x * scale)

    def __neg__(self) -> Self:
        return Point(-self.y, -self.x)


with open("inputs/day17.txt") as f:
    field = list(list(map(int, list(x.rstrip()))) for x in f.readlines())
    height = len(field)
    width = len(field[0])


def lookup(pos: Point) -> int | None:
    return field[pos.y][pos.x] if 0 <= pos.y < height and 0 <= pos.x < width else None


def is_goal(pos: Point) -> bool:
    return pos.y == height - 1 and pos.x == width - 1


def find_min_heat_loss_path(*, mindist: int = 1, maxdist: int = 1) -> int:
    # cost, position, invalid dir
    queue: list[tuple[int, Point, Point | None]] = [(0, Point(0, 0), None)]
    # maintain a set of seen states based on cost + position
    seen: set[tuple[int, Point | None]] = set()
    # maintain a lookup of poisition + direction running costs
    costs: dict[tuple[Point, Point]] = {}

    DIRS: tuple[Point] = (Point(0, 1), Point(1, 0), Point(0, -1), Point(-1, 0))

    while queue:
        cost, pos, invalid_dir = heapq.heappop(queue)
        if is_goal(pos):
            return cost
        if (pos, invalid_dir) in seen:
            continue
        seen.add((pos, invalid_dir))
        for next_dir in DIRS:
            # if we specify an invalid direction, we cannot advance and we cannot backtrack
            if invalid_dir and next_dir == invalid_dir or -next_dir == invalid_dir:
                continue

            # starting new cost looks at range [1, mindist)
            chain_cost: int = sum(
                c for d in range(1, mindist) if (c := lookup(pos + next_dir * d))
            )

            # walk through each possible distance contender from [mindist, maxdist]
            for distance in range(mindist, maxdist + 1):
                if c := lookup(next_pos := pos + next_dir * distance):
                    next_cost = cost + (chain_cost := chain_cost + c)
                    if costs.get((next_pos, next_dir), next_cost + 1) > next_cost:
                        costs[(next_pos, next_dir)] = next_cost
                        heapq.heappush(queue, (next_cost, next_pos, next_dir))


print(find_min_heat_loss_path(maxdist=3))
print(find_min_heat_loss_path(mindist=4, maxdist=10))
