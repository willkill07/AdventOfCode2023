from collections import Counter, defaultdict
import dataclasses


@dataclasses.dataclass
class Coord3D:
    x: int
    y: int
    z: int


@dataclasses.dataclass(kw_only=True)
class Data:
    z: int = -1
    index: int = -1


@dataclasses.dataclass
class Brick:
    start: Coord3D
    stop: Coord3D

    def xrange(self) -> range:
        return range(self.start.x, self.stop.x + 1)

    def yrange(self) -> range:
        return range(self.start.y, self.stop.y + 1)

    def zmove(self, fall_amount: int):
        if fall_amount > 0:
            self.start.z -= fall_amount
            self.stop.z -= fall_amount


def parse() -> list[Brick]:
    with open("inputs/day22.txt") as f:
        coord_from_str = lambda c: Coord3D(*map(int, c.split(",")))
        brick_from_str = lambda s: Brick(*map(coord_from_str, s.rstrip().split("~")))
        return sorted(list(map(brick_from_str, f.readlines())), key=lambda b: b.start.z)


def fall(bricks: list[Brick]) -> tuple[set[int], defaultdict[int, list[int]]]:
    highest: defaultdict[tuple[int, int], Data] = defaultdict(Data)
    bad: set[int] = set()
    graph: defaultdict[int, list[int]] = defaultdict(list)
    for idx, b in enumerate(bricks):
        max_z: int = -1
        support: set[int] = set()
        for x in b.xrange():
            for y in b.yrange():
                high: Data = highest[x, y]
                if high.z > max_z:
                    max_z, support = high.z, {high.index}
                elif high.z == max_z:
                    support.add(high.index)
        for x in support:
            graph[x].append(idx)
        if len(support) == 1:
            bad.update(support)
        b.zmove(b.start.z - max_z - 1)
        highest.update(
            ((x, y), Data(z=b.stop.z, index=idx))
            for x in b.xrange()
            for y in b.yrange()
        )
    return bad, graph


def count(idx: int, graph: defaultdict[int, list[int]]) -> int:
    degree: Counter[int] = Counter(i for g in graph.values() for i in g)
    count: int = -1
    q: list[int] = [idx]
    while q:
        count += 1
        adj: int = q.pop()
        degree.subtract(i for i in graph[adj])
        q.extend(i for i in graph[adj] if not degree[i])
    return count


bricks: list[Brick] = parse()
bad, graph = fall(bricks)
print(len(bricks) - len(bad) + 1)
print(sum(count(x, graph) for x in range(len(bricks))))
