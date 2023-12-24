import itertools
import re
import z3
import dataclasses


@dataclasses.dataclass(frozen=True)
class Hailstone:
    px: int
    py: int
    pz: int
    vx: int
    vy: int
    vz: int

    @property
    def vm(self) -> float:
        return self.vy / self.vx

    @property
    def pb(self) -> float:
        return self.py - self.vm * self.px


def parse() -> list[Hailstone]:
    with open("inputs/day24.txt") as input_file:
        return list(
            Hailstone(*(int(s) for s in re.findall(r"-?\d+", line)))
            for line in map(str.rstrip, input_file.readlines())
        )


def part1(hailstones: list[Hailstone]) -> int:
    lo, hi = 2 * 10**14, 4 * 10**14
    return sum(
        1
        for h1, h2 in itertools.combinations(hailstones, 2)
        if h1.vm != h2.vm
        and (((ix := (h2.pb - h1.pb) / (h1.vm - h2.vm)) - h1.px) / h1.vx) >= 0
        and (ix - h2.px) / h2.vx >= 0
        and lo <= ix <= hi
        and lo <= (h1.vm * ix + h1.pb) <= hi
    )


def part2(hailstones: list[Hailstone]) -> int:
    px, py, pz, vx, vy, vz = z3.Reals("px py pz vx vy vz")
    solver = z3.Solver()
    ts: list[z3.Real] = list(z3.Real(f"t{i}") for i, _ in enumerate(hailstones))
    solver.add(
        *(
            z3.And(
                t > 0,
                px + t * vx == h.px + t * h.vx,
                py + t * vy == h.py + t * h.vy,
                pz + t * vz == h.pz + t * h.vz,
            )
            for t, h in zip(ts, hailstones)
        )
    )
    solver.check()
    return sum(solver.model()[v].as_long() for v in (px, py, pz))


hailstones: list[Hailstone] = parse()
print(part1(hailstones))
print(part2(hailstones))
