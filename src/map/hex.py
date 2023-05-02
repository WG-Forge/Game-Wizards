class Hex:

    def __init__(self, q, r, s):
        self.q = q
        self.r = r
        self.s = s

    def __str__(self):
        return f"({self.q}, {self.r}, {self.s})"

    def __repr__(self):
        return f"({self.q}, {self.r}, {self.s})"

    def __hash__(self):
        return hash((self.q, self.r, self.s))

    def __eq__(self, other):
        return self.q == other.q and self.r == other.r and self.s == other.s

    def __lt__(self, other):
        sum_1 = abs(self.q) + abs(self.r) + abs(self.s)
        sum_2 = abs(other.q) + abs(other.r) + abs(other.s)
        return sum_1 < sum_2

    def __iter__(self):
        return iter((self.q, self.r, self.s))

    def __contains__(self, item: int):
        return self.q == item or self.r == item or self.s == item
