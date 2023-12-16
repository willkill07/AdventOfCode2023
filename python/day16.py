class Dirs:
    Left: complex = -1 + 0j
    Right: complex = 1 + 0j
    Up: complex = 0 - 1j
    Down: complex = 0 + 1j


def dfs_visit(
    field: dict[tuple[complex, complex], str], start: tuple[complex, complex]
) -> int:
    queue: list[tuple[complex, complex]] = list()
    visited: set[tuple[complex, complex]] = set()
    match start:
        case (start_pos, start_dir):
            queue.append((start_pos - start_dir, start_dir))
    while queue:
        curr_pos, d = queue.pop()
        while not (curr_pos, d) in visited:
            visited.add((curr_pos, d))
            curr_pos += d
            match field.get(curr_pos):
                case "|":
                    d = Dirs.Down
                    queue.append((curr_pos, Dirs.Up))
                case "-":
                    d = Dirs.Left
                    queue.append((curr_pos, Dirs.Right))
                case "/":
                    match d:
                        case Dirs.Left:
                            d = Dirs.Down
                        case Dirs.Right:
                            d = Dirs.Up
                        case Dirs.Up:
                            d = Dirs.Right
                        case Dirs.Down:
                            d = Dirs.Left
                case "\\":
                    match d:
                        case Dirs.Left:
                            d = Dirs.Up
                        case Dirs.Right:
                            d = Dirs.Down
                        case Dirs.Up:
                            d = Dirs.Left
                        case Dirs.Down:
                            d = Dirs.Right
                case None:
                    break

    return len(set(curr_pos for curr_pos, _ in visited)) - 1


pos = complex

field = dict(
    (pos(i, j), cell)
    for j, r in enumerate(open("inputs/day16.txt"))
    for i, cell in enumerate(r.strip())
)

print(dfs_visit(field, (pos(0, 0), Dirs.Right)))

print(
    max(
        map(
            lambda start: dfs_visit(field, start),
            (
                (start_pos, start_dir)
                for start_dir in (Dirs.Up, Dirs.Down, Dirs.Left, Dirs.Right)
                for start_pos in field
                if start_pos - start_dir not in field
            ),
        )
    )
)
