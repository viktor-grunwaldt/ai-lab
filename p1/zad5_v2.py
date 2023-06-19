import random
import numpy as np


def calc_dist(row, D):
    fst = 0
    lst = D

    ones = row.count(1)
    inframe = row[0:D].count(1)
    b4frame = 0
    afframe = ones - inframe
    ans = []

    if D == 0:
        return ones

    for _ in range(len(row) - D + 1):
        ans.append(D - inframe + b4frame + afframe)

        if row[fst] == 1:
            inframe = max(inframe - 1, 0)
            b4frame += 1

        if lst < len(row) and row[lst] == 1:
            inframe += 1
            afframe = max(afframe - 1, 0)

        # Move indiceies
        fst += 1
        lst += 1

    return min(ans)


class Nonogram:
    def __init__(self, rows, cols, row, col):
        self.rows = rows  # Number of rows
        self.cols = cols  # Number of cols
        self.row = row  # Rows description
        self.col = col  # Cols description
        self.nono = np.zeros((rows, cols))  # A board matrix
        self.MAXITER = 5000  # Max. number of iterations of solve()

    def toFile(self, fname):
        with open(fname, mode="w") as f:
            for row in self.nono:
                for v in row:
                    print("{}".format("#" if v == 1 else "."), end="", file=f)
                print(file=f)

    def opt_dist(self, row, d):
        return calc_dist(row.tolist(), d)

    def count_bad_rows(self):
        """
        Return indicies of incorrect rows
        """
        return [
            i for i, row in enumerate(self.nono) if self.opt_dist(row, self.row[i]) > 0
        ]

    def scoreColToggled(self, colno, pixno):
        """
        For a given column returns opt_dist(col, d) - opt_dist(col' - d),
        where col' is a col with toggled i-th bit

        rateColOnToggle > 0  iff pixel toggle improved col score
                        = 0  iff              hasn't changed anything
                        < 0  iff              made the score worse
        """
        col = np.copy(self.nono[:, colno])
        d = self.opt_dist(col, self.col[colno])

        col[pixno] = 1 if col[pixno] == 0 else 0
        d2 = self.opt_dist(col, self.col[colno])

        return d - d2

    def validateCols(self):
        for c in range(self.cols):
            if calc_dist(self.nono[:, c].tolist(), self.col[c]) > 0:
                return False
        return True

    def randDecision(self):
        return random.randrange(0, 99) < 20

    def solve(self):
        for _ in range(self.MAXITER):
            bad_rows = self.count_bad_rows()

            if not bad_rows:
                if self.validateCols():
                    return
                else:
                    row_num = random.randrange(0, self.rows)
            else:
                row_num = random.choice(bad_rows)

            # With probability 1/5 choose a random row
            if self.randDecision():
                row_num = random.randrange(0, self.rows)

            col_scores = [
                c
                for c in range(self.cols)
                if self.scoreColToggled(c, row_num) > 0 or self.randDecision()
            ]

            # Choose random column to toggle a pixel
            if not col_scores:
                col_num = random.randrange(0, self.cols - 1)
            else:
                col_num = random.choice(col_scores)

            # toggle
            self.nono[row_num][col_num] = 1 if self.nono[row_num][col_num] == 0 else 0

        self.solve()


if __name__ == "__main__":
    finput = "zad5_input.txt"
    foutput = "zad5_output.txt"

    lines = []
    with open(finput) as f:
        for line in f:
            lines.append(line)

    rows, cols = map(int, lines[0].strip().split(" "))

    row = [int(r) for r in lines[1 : rows + 1]]
    col = [int(c) for c in lines[cols + 1 :]]

    nono = Nonogram(rows, cols, row, col)
    nono.solve()
    nono.toFile(foutput)
