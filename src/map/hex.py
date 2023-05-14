from __future__ import annotations
import math

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, HEX_SIZE


class Hex:
    __hexDirectionVectors = [
        (1, 0, -1), (1, -1, 0), (0, -1, 1),
        (-1, 0, 1), (-1, 1, 0), (0, 1, -1),
    ]

    def __init__(self, q: int = None, r: int = None, s: int = None, t: tuple = None) -> None:
        if not t:
            self.q = q
            self.r = r
            self.s = s
        else:
            self.q, self.r, self.s = t

    def __str__(self) -> str:
        return f"({self.q}, {self.r}, {self.s})"

    def __repr__(self) -> str:
        return f"({self.q}, {self.r}, {self.s})"

    def __hash__(self) -> int:
        return hash((self.q, self.r, self.s))

    def __eq__(self, other: Hex) -> bool:
        return self.q == other.q and self.r == other.r and self.s == other.s

    def __lt__(self, other: Hex) -> bool:
        sum_1 = abs(self.q) + abs(self.r) + abs(self.s)
        sum_2 = abs(other.q) + abs(other.r) + abs(other.s)
        return sum_1 < sum_2

    def __iter__(self):
        return iter((self.q, self.r, self.s))

    def __contains__(self, item: int) -> bool:
        return self.q == item or self.r == item or self.s == item

    def __add__(self, other: Hex) -> Hex:
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)

    def __mul__(self, other: int) -> Hex:
        return Hex(self.q * other, self.r * other, self.s * other)

    def __abs__(self) -> int:
        return abs(self.q) + abs(self.r) + abs(self.s)

    @staticmethod
    def dict_to_hex(data: dict) -> Hex:
        return Hex(data['x'], data['y'], data['z'])

    @staticmethod
    def __hex_direction(direction: int) -> Hex:
        q, r, s = Hex.__hexDirectionVectors[direction]
        return Hex(q, r, s)

    @staticmethod
    def hex_neighbor(h: Hex, direction: int) -> Hex:
        return h + Hex.__hex_direction(direction)

    # Returns a list of a hexes that are in a ring on certain radius
    @staticmethod
    def hex_ring(center: Hex, radius: int) -> list[Hex]:
        results = []
        h = center + (Hex.__hex_direction(4) * radius)
        for i in range(6):
            for j in range(radius):
                results.append(h)
                h = Hex.hex_neighbor(h, i)

        return results

    # Returns a list of hexes that are in a spiral on certain radius
    @staticmethod
    def hex_spiral(center: Hex, radius: int) -> list[Hex]:
        results = [center]
        for k in range(radius):
            results += Hex.hex_ring(center, k)

        return results

    # Function that converts cubic coordinates to pixel coordinates
    @staticmethod
    def hex_to_pixel(q: int, r: int) -> tuple:
        screen_x = HEX_SIZE * 3 / 2 * r
        screen_y = HEX_SIZE * math.sqrt(3) * (q + r / 2)

        return int(screen_x + SCREEN_WIDTH / 2), int(screen_y + SCREEN_HEIGHT / 2)

    @staticmethod
    def distance(h1: Hex, h2: Hex) -> int:
        return int((abs(h1.q - h2.q) + abs(h1.r - h2.r) + abs(h1.s - h2.s)) / 2)

    @staticmethod
    def get_center(h: Hex) -> list[tuple]:
        x, y = Hex.hex_to_pixel(h.q, h.r)
        points = [(x + HEX_SIZE * math.cos(angle), y + HEX_SIZE * math.sin(angle))
                  for angle in [0, math.pi / 3, 2 * math.pi / 3, math.pi, 4 * math.pi / 3, 5 * math.pi / 3]
                  ]
        return points
