import math

dir_to_step: dict[str, tuple[int, int]] = {
        "^": (-1, 0),
        "<": (0, -1),
        "v": (1, 0),
        ">": (0, 1),
}

next_dir_dict: dict[tuple[str, str], str] = {
        ("|", "^"): "^",
        ("|", "v"): "v",
        ("-", "<"): "<",
        ("-", ">"): ">",
        ("L", "v"): ">",
        ("L", "<"): "^",
        ("J", "v"): "<",
        ("J", ">"): "^",
        ("7", "^"): "<",
        ("7", ">"): "v",
        ("F", "^"): ">",
        ("F", "<"): "v",
}

pipe_characters: set[str] = {"|", "-", "L", "J", "7", "F"}

def connects(dir: str, pipe: str) -> bool:
    return next_dir_dict.get((pipe, dir)) is not None

def next_dir(dir: str, pipe: str) -> str:
    return next_dir_dict[(pipe, dir)]

def add_tuples(t1, t2) -> tuple[int, int]:
    return tuple(i1 + i2 for i1, i2 in zip(t1, t2))

def set_idx(idx: tuple[int, int], character: str):
    lines[idx[0]][idx[1]] = character

def get_idx(idx: tuple[int, int]) -> str:
    return lines[idx[0]][idx[1]]

def idx_in_grid(idx: tuple[int, int]) -> bool:
    return 0 <= idx[0] and idx[0] < len(lines) and 0 <= idx[1] and idx[1] < len(lines[0])

with open('inputs/day10.txt') as f:
    lines = list(map(str.rstrip, f.readlines()))

s_idx = (0, 0)
for i, line in enumerate(lines):
    for j, character in enumerate(line):
        if character == "S":
            s_idx = (i, j)

integral = 0

pos: tuple[str, tuple[int, int]] = ("", (0,0))

for dir, step in dir_to_step.items():
    next_idx = add_tuples(s_idx, step)
    next_character = get_idx(next_idx)
    if next_character in pipe_characters and connects(dir, next_character):
        pos = (next_dir_dict[(next_character, dir)], next_idx)
        integral -= step[1] * next_idx[0]
        break

steps = 1
while True:
    steps += 1
    dir, idx = pos
    character = get_idx(idx)

    step = dir_to_step[dir]
    next_idx = add_tuples(idx, step)
    integral -= step[1] * next_idx[0]
    if not idx_in_grid(next_idx):
        break

    next_character = get_idx(next_idx)
    if next_character == "S":
        net = abs(integral) - int(steps/2) + 1
        print(f"Part 1 answer: {math.ceil(steps / 2)}")
        print(f"Part 2 answer: {net}")
        break

    if not(next_character in pipe_characters and connects(dir, next_character)):
        break

    pos = (next_dir_dict[(next_character, dir)], next_idx)