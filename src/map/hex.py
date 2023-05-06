class Hex:

    def __init__(self, q: int, r: int, s: int) -> None:
        self.q = q
        self.r = r
        self.s = s

    def __str__(self) -> str:
        return f"({self.q}, {self.r}, {self.s})"

    def __repr__(self) -> str:
        return f"({self.q}, {self.r}, {self.s})"

    def __hash__(self) -> int:
        return hash((self.q, self.r, self.s))

    def __eq__(self, other) -> bool:
        return self.q == other.q and self.r == other.r and self.s == other.s

    def __lt__(self, other) -> bool:
        sum_1 = abs(self.q) + abs(self.r) + abs(self.s)
        sum_2 = abs(other.q) + abs(other.r) + abs(other.s)
        return sum_1 < sum_2

    def __iter__(self):
        return iter((self.q, self.r, self.s))

    def __contains__(self, item: int) -> bool:
        return self.q == item or self.r == item or self.s == item
