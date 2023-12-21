import math
from dataclasses import dataclass, field
from abc import abstractmethod
from collections import defaultdict, deque
import operator
from typing import Any, Final, Iterable


@dataclass(frozen=True)
class Pulse:
    value: bool = False

    @staticmethod
    def flip(p: "Pulse") -> "Pulse":
        return Pulse(not p.value)


HI: Final[Pulse] = Pulse(True)
LO: Final[Pulse] = Pulse(False)


@dataclass
class Module:
    name: str
    state: Pulse = LO
    txs: list[str] = field(default_factory=list)
    rxs: set[str] = field(default_factory=set)

    @abstractmethod
    def rx(self, src: str, p: Pulse, press: int) -> Iterable[tuple[str, str, Pulse]]:
        raise NotImplemented()

    def tx(self, p: Pulse) -> Iterable[tuple[str, str, Pulse]]:
        return ((self.name, output, p) for output in self.txs)


@dataclass
class FlipFlopModule(Module):
    def rx(self, src: str, p: Pulse, press: int) -> Iterable[tuple[str, str, Pulse]]:
        if p == HI:
            return ()
        self.state = Pulse.flip(self.state)
        return self.tx(self.state)


@dataclass
class Conjunction(Module):
    ins: defaultdict[str, Pulse] = field(default_factory=lambda: defaultdict(Pulse))
    his: defaultdict[str, list[int]] = field(default_factory=lambda: defaultdict(list))

    def rx(self, src: str, p: Pulse, press: int) -> Iterable[tuple[str, str, Pulse]]:
        self.ins[src] = p
        if self.ins[src] == HI:
            self.his[src].append(press)
        return self.tx(Pulse(not all(self.ins[name] == HI for name in self.rxs)))


@dataclass
class Broadcast(Module):
    def rx(self, src: str, p: Pulse, press: int) -> Iterable[tuple[str, str, Pulse]]:
        return self.tx(p)


@dataclass
class Machine(Module):
    def rx(self, src: str, p: Pulse, press: int) -> Iterable[tuple[str, str, Pulse]]:
        return ()


with open("inputs/day20.txt") as file:
    modules: dict[str, Module] = dict()
    inputs: defaultdict[str, set[str]] = defaultdict(set)
    for line in file.readlines():
        name, rhs = line.strip().split(" -> ")
        txs = rhs.split(", ")
        if line[0] == "%":
            name = name[1:]
            modules[name] = FlipFlopModule(name=name, txs=txs)
        elif line[0] == "&":
            name = name[1:]
            modules[name] = Conjunction(name=name, txs=txs)
        elif name == "broadcaster":
            modules[name] = Broadcast(name=name, txs=txs)

        for module in txs:
            inputs[module].add(name)

        modules["rx"] = Machine("rx")
        for name, m in modules.items():
            m.rxs = inputs[name]


def get_rxs(name: str) -> set[str]:
    return modules[name].rxs


def get_rx(name: str) -> str:
    return next(iter(get_rxs(name)))


def part1() -> int:
    t: tuple[int, int] = (0, 0)
    for _ in range(1000):
        match (t, push_button(modules)):
            case (lo1, hi1), (lo2, hi2):
                t = (lo1 + lo2, hi1 + hi2)
    return operator.mul(*t)


def part2() -> int:
    checks: set[str] = set(map(get_rx, modules[get_rx("rx")].rxs))
    assert len(checks) == 4
    for m in checks:
        assert isinstance(modules[m], Conjunction)
    presses: int = 1
    nums: defaultdict[str, set[int]] = defaultdict(set)
    while checks:
        push_button(modules, presses)
        to_remove = set()
        for m in checks:
            if len(his := modules[m].his.values()) == len(get_rxs(m)) and all(
                len(p) >= 2 for p in his
            ):
                nums[m] = nums[m].union(b - a for a, b, *_ in his)
                to_remove.add(m)
        checks -= to_remove
        presses += 1
    return math.lcm(*(max(n) for n in nums.values()))


def push_button(modules: dict[str, Module], press: int = 0):
    hi, lo = 0, 1
    q: deque[tuple[str, str, Pulse]] = deque()
    q.extend(modules["broadcaster"].tx(LO))
    while q:
        src, dst, p = q.popleft()
        if p == HI:
            hi += 1
        else:
            lo += 1
        q.extend(modules[dst].rx(src, p, press))
    return lo, hi


print(part1())
print(part2())
