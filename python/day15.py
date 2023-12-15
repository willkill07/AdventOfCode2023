from functools import reduce

with open("inputs/day15.txt") as f:
    lines = f.read().strip().split(",")


def my_hash(l: str) -> int:
    return reduce(lambda h, v: 17 * (h + ord(v)) & 255, l, 0)


def simulate(lines: list[str]) -> list[dict[str, int]]:
    boxes: list[dict[str, int]] = list(dict() for _ in range(256))
    for step in lines:
        match step.strip("-").split("="):
            case [l, f]:
                boxes[my_hash(l)][l] = int(f)
            case [l]:
                boxes[my_hash(l)].pop(l, 0)
    return boxes


boxes: list[dict[str, int]] = simulate(lines)

print(sum(map(my_hash, lines)))
print(
    sum(
        num * dist * focal
        for num, b in enumerate(boxes, 1)
        for dist, focal in enumerate(b.values(), 1)
    )
)
