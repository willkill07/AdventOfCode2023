import math
from typing import Callable, Iterable, NamedTuple, Self
import operator


class Part(NamedTuple):
    x: int
    m: int
    a: int
    s: int

    @property
    def rating(self: Self) -> int:
        return sum(self._asdict().values())


class RangePart(NamedTuple):
    x: range
    m: range
    a: range
    s: range

    @property
    def empty(self: Self) -> bool:
        return not all(self._asdict().values())

    @property
    def size(self: Self) -> int:
        return math.prod(map(len, self._asdict().values()))

    def _apply(
        self: Self,
        func: Callable[[range, int], tuple[range, range]],
        name: str,
        value: int,
    ):
        a, b = self._asdict(), self._asdict()
        a[name], b[name] = func(a[name], value)
        return RangePart(**a), RangePart(**b)

    def lt(self: Self, name: str, value: int):
        return self._apply(
            lambda r, v: (range(r.start, v), range(v, r.stop))
            if v in r
            else (range(0), r),
            name,
            value,
        )

    def gt(self: Self, name: str, value: int):
        return self._apply(
            lambda r, v: (range(v + 1, r.stop), range(r.start, v + 1))
            if v in r
            else (range(0), r),
            name,
            value,
        )


class Rule(NamedTuple):
    var: str
    op: str
    value: int
    target: str


OPS1: dict[str, Callable[[int, int], bool]] = {
    ">": operator.gt,
    "<": operator.lt,
}
OPS2: dict[str, Callable[[RangePart, str, int], tuple[RangePart, RangePart]]] = {
    ">": RangePart.gt,
    "<": RangePart.lt,
}


def parse(filename: str) -> tuple[dict[str, list[str | Rule]], list[Part]]:
    with open(filename) as f:
        rs, ps = list(map(lambda l: l.split("\n"), f.read().rstrip().split("\n\n")))

    def make_defs(defs: str) -> Iterable[str | Rule]:
        for d in defs.split(","):
            if ":" in d:
                cond, target = d.split(":")
                if ">" in cond:
                    name, value = cond.split(">")
                    yield Rule(name, ">", int(value), target)
                else:
                    name, value = cond.split("<")
                    yield Rule(name, "<", int(value), target)
            else:
                yield d

    def make_rule(rule: str) -> tuple[str, list[str | Rule]]:
        name, defs = rule[:-1].split("{")
        return (name, list(make_defs(defs)))

    def make_rules() -> dict[str, list[str | Rule]]:
        return dict(make_rule(r) for r in rs)

    def make_part(part: str) -> Iterable[tuple[str, int]]:
        for item in part[1:-1].split(","):
            name, value = item.split("=")
            yield (name, int(value))

    def make_parts() -> list[Part]:
        return list(Part(**dict(make_part(part))) for part in ps)

    return dict(make_rules()), make_parts()


def solve1(rules: dict[str, list[str | Rule]], part: Part, name: str = "in") -> bool:
    match name:
        case "A":
            return True
        case "R":
            return False
        case _:
            for rule in rules[name]:
                match rule:
                    case Rule(var, op, value, target):
                        if OPS1[op](getattr(part, var), value):
                            return solve1(rules, part, target)
                    case _:
                        return solve1(rules, part, rule)
            return False


def solve2(
    rules: dict[str, list[str | Rule]], part: RangePart, name: str = "in"
) -> Iterable[int]:
    if part.empty:
        return
    match name:
        case "R":
            return
        case "A":
            yield part.size
            return
    for rule in rules[name]:
        match rule:
            case Rule(var, op, value, target):
                a, part = OPS2[op](part, var, value)
                yield from solve2(rules, a, target)
            case _:
                yield from solve2(rules, part, rule)


rules, parts = parse("inputs/day19.txt")
print(sum(part.rating for part in parts if solve1(rules, part)))
print(sum(solve2(rules, RangePart(*[range(1, 4001)] * 4))))
