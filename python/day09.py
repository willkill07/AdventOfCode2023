with open("inputs/day09.txt") as f:
    inputs = list(map(lambda x: list(map(int, x.split())), f.readlines()))


def part1(nums):
    return (
        0
        if all(y == 0 for y in nums)
        else nums[-1] + part1(list(nums[i + 1] - nums[i] for i in range(len(nums) - 1)))
    )


def part2(nums):
    return (
        0
        if all(y == 0 for y in nums)
        else nums[0] - part2(list(nums[i + 1] - nums[i] for i in range(len(nums) - 1)))
    )


print(sum(map(part1, inputs)))
print(sum(map(part2, inputs)))
