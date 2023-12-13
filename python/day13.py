boards: list[list[list[str]]] = list(
    map(list, map(str.split, open("inputs/day13.txt").read().split("\n\n")))
)


def transpose(p: list[list[str]]) -> list[list[str]]:
    return list(map(list, zip(*p)))


def solve(board: list[list[str]], smudges: int = 0):
    try:
        return next(
            mirror
            for mirror in range(len(board))
            if (
                smudges
                == sum(
                    (l != r)
                    for lhs, rhs in zip(board[mirror - 1 :: -1], board[mirror:])
                    for l, r in zip(lhs, rhs)
                )
            )
        )
    except:
        return 0


for smudges in 0, 1:
    print(
        sum(
            100 * solve(board, smudges) + solve(transpose(board), smudges)
            for board in boards
        )
    )
