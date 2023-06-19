from more_itertools import flatten
from string import ascii_uppercase

kw = [["."] * 70 for _ in range(70)]
dirs = [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2), (2, 0), (0, 2), (2, 1), (2, 2)]
for l, (dx, dy) in zip(reversed(range(24)), dirs):
    for i in range(l):
        for j in range(l):
            kw[i + 24 * dx][j + 24 * dy] = ascii_uppercase[l]


print("\n".join("".join(line) for line in kw))

print(sum(1 for c in flatten(kw) if c == "."))
