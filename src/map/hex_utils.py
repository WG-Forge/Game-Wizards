import math

from src.map.hex import Hex


class HexUtils:

    __WIDTH, __HEIGHT = 1200, 800
    __HEX_SIZE = 21

    hexDirectionVectors = [
        Hex(1, 0, -1), Hex(1, -1, 0), Hex(0, -1, 1),
        Hex(-1, 0, 1), Hex(-1, 1, 0), Hex(0, 1, -1),
    ]

    @staticmethod
    def dict_to_hex(data: dict) -> Hex:
        return Hex(data['x'], data['y'], data['z'])

    @staticmethod
    def __hex_direction(direction: int) -> Hex:
        return HexUtils.hexDirectionVectors[direction]

    @staticmethod
    def __hex_add(h: Hex, vector: Hex) -> Hex:
        return Hex(h.q + vector.q, h.r + vector.r, h.s + vector.s)

    @staticmethod
    def hex_neighbor(h: Hex, direction: int) -> Hex:
        return HexUtils.__hex_add(h, HexUtils.__hex_direction(direction))

    @staticmethod
    def __hex_scale(h: Hex, factor: int) -> Hex:
        return Hex(h.q * factor, h.r * factor, h.s * factor)

    # Returns a list of a hexes that are in a ring on certain radius
    @staticmethod
    def hex_ring(center: Hex, radius: int) -> list[Hex]:
        results = []
        h = HexUtils.__hex_add(center, HexUtils.__hex_scale(HexUtils.__hex_direction(4), radius))
        for i in range(6):
            for j in range(radius):
                results.append(h)
                h = HexUtils.hex_neighbor(h, i)

        return results

    # Returns a list of hexes that are in a spiral on certain radius
    @staticmethod
    def hex_spiral(center: Hex, radius: int) -> list[Hex]:
        results = [center]
        for k in range(radius):
            results += HexUtils.hex_ring(center, k)

        return results

    # Function that converts pixel coordinates to cubic coordinates
    @staticmethod
    def __pixel_to_hex(x: int, y: int) -> Hex:
        r = 2 * x / HexUtils.__HEX_SIZE / 3
        q = y / HexUtils.__HEX_SIZE / math.sqrt(3) - r / 2
        s = -q - r

        return Hex(q, r, s)

    # Function that converts cubic coordinates to pixel coordinates
    @staticmethod
    def hex_to_pixel(q: int, r: int) -> tuple:
        screen_x = HexUtils.__HEX_SIZE * 3 / 2 * r
        screen_y = HexUtils.__HEX_SIZE * math.sqrt(3) * (q + r / 2)

        return int(screen_x + HexUtils.__WIDTH / 2), int(screen_y + HexUtils.__HEIGHT / 2)

    @staticmethod
    def distance(h1: Hex, h2: Hex) -> int:
        return int((abs(h1.q - h2.q) + abs(h1.r - h2.r) + abs(h1.s - h2.s)) / 2)
