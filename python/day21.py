from typing import Final

GARDEN_SIZE: Final[int] = 131
REAL_STEPS: Final[int] = 26_501_365

garden: dict[complex, str] = {
    complex(i, j): c
    for i, r in enumerate(open("inputs/day21.txt"))
    for j, c in enumerate(r)
    if c in ".S"
}


def cmod(x: complex) -> complex:
    return complex(x.real % GARDEN_SIZE, x.imag % GARDEN_SIZE)


def step(frontier: set[complex], *, count: int = 1) -> set[complex]:
    for _ in range(count):
        frontier = {
            p + d for d in (1, -1, 1j, -1j) for p in frontier if cmod(p + d) in garden
        }
    return frontier


def quadratic_fit(x: int, a: int, b: int, c: int) -> int:
    bma = b - a
    cmb = c - b
    return a + x * bma + x * (x - 1) // 2 * (cmb - bma)


reached: set[complex] = {loc for loc, item in garden.items() if item == "S"}
reached = step(reached, count=64)
print(len(reached))
print(
    quadratic_fit(
        REAL_STEPS // GARDEN_SIZE,
        len(reached := step(reached)),
        len(reached := step(reached, count=GARDEN_SIZE)),
        len(reached := step(reached, count=GARDEN_SIZE)),
    )
)
