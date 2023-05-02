import pygame
import math
import random

from src.map.hex import Hex
from src.vehicles.tank import Tank


class Map:
    WIDTH, HEIGHT = 1200, 800
    HEX_SIZE = 21

    hexDirectionVectors = [
        Hex(1, 0, -1), Hex(1, -1, 0), Hex(0, -1, 1),
        Hex(-1, 0, 1), Hex(-1, 1, 0), Hex(0, 1, -1),
    ]

    __BLACK = (0, 0, 0)
    __WHITE = (255, 255, 255)
    __GRAY = (127, 127, 127)
    __HP_GREEN = (2, 113, 72)
    __RED = (255, 0, 0)
    __BASE_GREEN = (144, 238, 144)
    __TANK_RED = (237, 41, 57)
    __SPAWN_RED = (255, 198, 196)
    __TANK_BLUE = (70, 191, 224)
    __SPAWN_BLUE = (173, 216, 230)
    __TANK_YELLOW = (224, 206, 70)
    __SPAWN_YELLOW = (255, 250, 205)

    def __init__(self, game_map: dict, game_state: dict, players_in_game: dict) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((Map.WIDTH, Map.HEIGHT))
        pygame.display.set_caption("Game Wizards")
        self.__font_size = 24
        self.__font = pygame.font.Font(None, self.__font_size)

        self.__map: [Hex] = []
        self.__tanks: dict[int, Tank] = {}
        self.__tank_positions: dict[int, Hex] = {}
        self.__spawn_points: [Hex] = []

        self.__base: [Hex] = []
        self.__obstacles: [Hex] = []
        self.__light_repair: [Hex] = []
        self.__heavy_repair: [Hex] = []
        self.__catapult: dict[Hex, int] = {}

        self.__destroyed: [Tank] = []
        self.__shoot_actions: dict[int, []] = {}
        self.__player_ids: [int] = []
        self.__initialize_map(game_map, game_state, players_in_game)

    def __initialize_map(self, game_map: dict, game_state: dict, players_in_game: dict) -> None:
        self.__map = self.__hexSpiral(Hex(0, 0, 0), game_map["size"])

        for p in players_in_game.keys():
            self.__player_ids.append(p)

        for idx in self.__player_ids:
            self.__shoot_actions[idx] = []

        for tank_id, tank_info in game_state["vehicles"].items():
            player = players_in_game[tank_info["player_id"]]
            tank = Tank(int(tank_id), tank_info)
            self.__tanks[int(tank_id)] = tank
            player.add_tank(tank)
            self.__spawn_points.append(self.fromDictToHex(tank_info["spawn_position"]))

        for player in players_in_game.values():
            if not player.is_observer:
                player.reorder()

        for h, positions in game_map["content"].items():
            for position in positions:
                new_hex = Map.fromDictToHex(position)
                if h == "base":
                    self.__base.append(new_hex)
                elif h == "obstacle":
                    self.__obstacles.append(new_hex)
                elif h == "light_repair":
                    self.__light_repair.append(new_hex)
                elif h == "hard_repair":
                    self.__heavy_repair.append(new_hex)
                elif h == "catapult":
                    self.__catapult[new_hex] = 3

    def draw(self, current_turn: int, num_turns: int):
        self.screen.fill(Map.__WHITE)
        text = self.__font.render(f"ROUND NUMBER: {current_turn + 1}/{num_turns}", True, Map.__BLACK)
        self.screen.blit(text, (30, 25))

        for h in self.__map:
            # coordinates of the center of the hex
            x, y = Map.hexToPixel(h.q, h.r)

            points = [(x + Map.HEX_SIZE * math.cos(angle), y + Map.HEX_SIZE * math.sin(angle))
                      for angle in [0, math.pi / 3, 2 * math.pi / 3, math.pi, 4 * math.pi / 3, 5 * math.pi / 3]
                      ]
            pygame.draw.polygon(self.screen, Map.__BLACK, points, 3)

            # obstacle coloring
            if h in self.__obstacles:
                pygame.draw.polygon(self.screen, Map.__GRAY, points, 0)
                pygame.draw.polygon(self.screen, Map.__BLACK, points, 3)

            # base coloring
            if h in self.__base:
                pygame.draw.polygon(self.screen, Map.__BASE_GREEN, points, 0)
                pygame.draw.polygon(self.screen, Map.__BLACK, points, 3)

            # blue spawn coloring
            if h.s == 10 and -7 <= h.q <= -3 and -7 <= h.r <= -3:
                pygame.draw.polygon(self.screen, Map.__SPAWN_BLUE, points, 0)
                pygame.draw.polygon(self.screen, Map.__BLACK, points, 3)

            # orange spawn coloring yellow
            elif h.q == 10 and -7 <= h.s <= -3 and -7 <= h.r <= -3:
                pygame.draw.polygon(self.screen, Map.__SPAWN_YELLOW, points, 0)
                pygame.draw.polygon(self.screen, Map.__BLACK, points, 3)

            # purple spawn coloring red
            elif h.r == 10 and -7 <= h.s <= -3 and -7 <= h.q <= -3:
                pygame.draw.polygon(self.screen, Map.__SPAWN_RED, points, 0)
                pygame.draw.polygon(self.screen, Map.__BLACK, points, 3)

        self.__draw_special(self.__catapult.keys(), "catapult")
        self.__draw_special(self.__heavy_repair, "heavy_repair")
        self.__draw_special(self.__light_repair, "light_repair")

        for t in self.__tanks.values():
            self.__draw_tank(t)

        self.__draw_hp()
        self.__draw_legend()

        pygame.display.flip()

    def update_map(self, game_state: dict) -> None:
        for tank_id, tank_info in game_state["vehicles"].items():
            tank_id = int(tank_id)
            self.__tank_positions[tank_id] = Map.fromDictToHex(tank_info["position"])
            server_position = Map.fromDictToHex(tank_info["position"])
            server_hp = tank_info["health"]
            server_cp = tank_info["capture_points"]

            tank = self.__tanks[tank_id]
            tank_position = tank.get_position()
            tank_hp = tank.get_hp()
            tank_cp = tank.get_cp()

            if server_position != tank_position:
                self.local_move(tank, server_position)
            if server_hp != tank_hp:
                tank.update_hp(server_hp)
            if server_cp != tank_cp:
                tank.update_cp(server_cp)

    def __draw_legend(self) -> None:
        pass

    def __draw_special(self, hexes: [Hex], name: str) -> None:
        image = pygame.image.load(f"src/assets/special_hexes/{name}.png")
        scaled_image = pygame.transform.scale(image, (28, 28))
        for h in hexes:
            x, y = self.hexToPixel(h.q, h.r)
            self.screen.blit(scaled_image, (x - 14, y - 14))

    def __draw_tank(self, tank: Tank) -> None:
        image = pygame.image.load(f"src/assets/vehicle_types/{tank.get_type()}.png")
        scaled_image = pygame.transform.scale(image, (28, 28))
        h, idx = tank.get_position(), tank.get_player_id()
        if idx == self.__player_ids[0]:
            color_tuple = Map.__TANK_BLUE
        elif idx == self.__player_ids[1]:
            color_tuple = Map.__TANK_RED
        else:
            color_tuple = Map.__TANK_YELLOW
        color = pygame.Surface(scaled_image.get_size())
        color.fill(color_tuple)
        scaled_image.blit(color, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        x, y = self.hexToPixel(h.q, h.r)
        self.screen.blit(scaled_image, (x - 14, y - 14))

    def __draw_hp(self) -> None:
        for tank in self.__tanks.values():
            ratio_green = tank.get_hp() * 1.0 / tank.get_full_hp()
            q, r = tank.get_position().q, tank.get_position().r
            x, y = self.hexToPixel(q, r)
            line_start_g = (x - 10, y - 13)
            line_end_g = (x + 10 * ratio_green, y - 13)
            line_start_r = line_end_g
            line_end_r = (x + 10, y - 13)
            pygame.draw.line(self.screen, Map.__HP_GREEN, line_start_g, line_end_g, 4)
            if ratio_green != 1.0:
                pygame.draw.line(self.screen, Map.__RED, line_start_r, line_end_r, 4)

    def draw_shoot_animation(self, tank: Tank, tanks: list[Tank]) -> None:
        h1 = tank.get_position()
        for t in tanks:
            h2 = t.get_position()
            x1, y1 = Map.hexToPixel(h1.q, h1.r)
            x2, y2 = Map.hexToPixel(h2.q, h2.r)
            points = [(x2 + Map.HEX_SIZE * math.cos(angle), y2 + Map.HEX_SIZE * math.sin(angle))
                      for angle in [0, math.pi / 3, 2 * math.pi / 3, math.pi, 4 * math.pi / 3, 5 * math.pi / 3]
                      ]
            pygame.draw.polygon(self.screen, Map.__RED, points, 3)
            pygame.draw.line(self.screen, Map.__RED, (x1, y1), (x2, y2), 5)

        pygame.display.flip()

    def draw_attacked_hp(self, tanks: [Tank], damage: int) -> None:
        for t in tanks:
            new_hp = t.get_hp() - damage
            if new_hp < 0:
                new_hp = 0
            ratio_green = new_hp * 1.0 / t.get_full_hp()
            q, r = t.get_position().q, t.get_position().r
            x, y = self.hexToPixel(q, r)
            line_start_g = (x - 10, y - 13)
            line_end_g = (x + 10 * ratio_green, y - 13)
            line_start_r = line_end_g
            line_end_r = (x + 10, y - 13)
            if ratio_green != 0:
                pygame.draw.line(self.screen, Map.__HP_GREEN, line_start_g, line_end_g, 4)
            elif ratio_green == 0:
                line_start_r = line_start_g
            pygame.draw.line(self.screen, Map.__RED, line_start_r, line_end_r, 4)

        pygame.display.flip()

    def hex_reachable(self, start: Hex, movement: int) -> Hex:
        visited = []
        rings = [[start]]
        for k in range(1, movement + 1):
            rings.append([])
            for h in rings[k - 1]:
                for direction in range(6):
                    neighbor = self.__hexNeighbor(h, direction)
                    if neighbor not in visited and neighbor not in self.__obstacles \
                            and not self.__offTheGridDetection(neighbor):
                        visited.append(neighbor)
                        rings[k].append(neighbor)

        visited = [h for h in visited if h not in self.__spawn_points and h not in self.__tank_positions.values()]
        visited.sort(key=lambda x: x)

        move_to = []
        if visited:
            d = self.distance(Hex(0, 0, 0), visited[0])
            move_to = [h for h in visited if self.distance(Hex(0, 0, 0), h) == d]

        return random.choice(move_to) if visited else None

        # return visited[0] if visited else None

    def catapult_check(self, tank: Tank, move_coord: Hex) -> None:
        if move_coord in self.__catapult.keys() and self.__catapult[move_coord] > 0:
            tank.set_bonus_range(1)
            self.__catapult[move_coord] -= 1

    def heavy_repair_check(self, tank: Tank, move_coord: Hex) -> None:
        tank_type = tank.get_type()
        if (tank_type == "heavy_tank" or tank_type == "at_spg") and move_coord in self.__heavy_repair:
            tank.repair()

    def light_repair_check(self, tank: Tank, move_coord: Hex) -> None:
        tank_type = tank.get_type()
        if tank_type == "medium_tank" and move_coord in self.__light_repair:
            tank.repair()

    def local_move(self, tank: Tank, coord: Hex) -> None:
        self.__tank_positions[tank.get_id()] = coord
        tank.update_position(coord)

    def local_shoot(self, tank: Tank, tank2: Tank) -> None:
        if tank2.get_hp() - tank.get_damage() <= 0:
            tank.update_cp(tank.get_cp() + tank2.get_full_hp())
            tank2.reset()
        else:
            tank2.update_hp(tank2.get_hp() - tank.get_damage())

        self.__shoot_actions[tank.get_player_id()].append(tank2.get_player_id())

    def reset_shoot_actions(self, player_id: int) -> None:
        self.__shoot_actions[player_id] = []

    def tank_from_hex(self, h: Hex) -> Tank:
        return self.__tanks[Map.get_key_from_value(self.__tank_positions, h)[0]]

    @staticmethod
    def get_key_from_value(d, value):
        return [k for k, v in d.items() if v == value]

    def shoot(self, tank: Tank) -> [Hex, [Tank]]:
        if tank.get_type() != "at_spg":
            return self.__curved_trajectory(tank)
        else:
            return self.__straight_trajectory(tank)

    def __curved_trajectory(self, tank: Tank) -> [Hex, [Tank]]:
        # Shoot coords based on tank position
        shoot_coords = self.__shoot_coords(tank)

        # Blocked hexes
        blocked = []

        # Add obstacles to blocked
        for coord in shoot_coords:
            if coord in self.__obstacles:
                blocked.append(coord)

        # Add to blocked my and neutral tanks
        for t in self.__tanks.values():
            if t.get_player_id() == tank.get_player_id() or self.neutrality_check(tank, t):
                blocked.append(t.get_position())

        # Enemy tanks
        enemy_tanks = []

        # Add enemy tanks to list
        for t in self.__tanks.values():
            if t.get_position() not in blocked:
                enemy_tanks.append(t.get_position())

        # Keep only coords that are not blocked and in enemy_tanks
        shoot_coords = [coord for coord in shoot_coords if coord not in blocked and coord in enemy_tanks]

        # From hex list make tank list
        tank_shoot_coords = [self.tank_from_hex(h) for h in shoot_coords]

        # Keep tanks whose hp is > 0 and sort them based on hp
        tank_shoot_coords = [t for t in tank_shoot_coords if t.get_hp() > 0]
        tank_shoot_coords.sort(key=lambda tt: tt)

        # Shoot at tank with the lowest hp
        if tank_shoot_coords:
            return tank_shoot_coords[0].get_position(), [tank_shoot_coords[0]]
        else:
            return None, None

    def __straight_trajectory(self, tank: Tank) -> [Hex, [Tank]]:
        # Shoot coords based on tank position
        shoot_coords = self.__shoot_coords(tank)
        x, y, z = tank.get_position()

        # Blocked hexes
        blocked = []

        # Add obstacles to blocked
        for coord in shoot_coords:
            if coord in self.__obstacles:
                blocked.append(coord)
                d = Map.distance(tank.get_position(), coord)
                (dx, dy, dz) = ((x - coord.q) / d, (y - coord.r) / d, (z - coord.s) / d)
                for i in range(tank.get_max_range() - d):
                    blocked.append(Hex(coord.q - (i + 1) * dx, coord.r - (i + 1) * dy, coord.s - (i + 1) * dz))

        # Add to blocked my tanks that are not in 1st ring and neutral (if in 1st ring add whole line)
        for t in self.__tanks.values():
            coord = t.get_position()
            if t.get_player_id() == tank.get_player_id() and self.distance(coord, tank.get_position()) > 1:
                blocked.append(coord)
            elif self.neutrality_check(tank, t):
                if self.distance(coord, tank.get_position()) == 1:
                    blocked.append(coord)
                    (dx, dy, dz) = ((x - coord.q), (y - coord.r), (z - coord.s))
                    for i in range(tank.get_max_range()):
                        blocked.append(Hex(x - (i + 1) * dx, y - (i + 1) * dy, z - (i + 1) * dz))
                else:
                    blocked.append(t.get_position())

        # Keep only coords that are not blocked
        shoot_coords = [coord for coord in shoot_coords if coord not in blocked]

        # Enemy tanks
        enemy_tanks = []

        # Add enemy tanks to list
        for t in self.__tanks.values():
            if t.get_player_id() != tank.get_player_id() and not self.neutrality_check(tank, t):
                enemy_tanks.append(t)

        # Only keep enemies that are in shoot range whose hp is > 0 and sort them based on hp
        enemy_tanks = [t for t in enemy_tanks if t.get_position() in shoot_coords and t.get_hp() > 0]
        enemy_tanks.sort(key=lambda tt: tt)

        # If there are enemy tanks shoot in line where tank with the lowest hp is
        if enemy_tanks:
            tank_shot = enemy_tanks[0]
        else:
            return None, None

        # List of tanks being shot
        tanks_shot_at = []

        # Add to tanks_shot_at
        coord = tank_shot.get_position()
        d = Map.distance(tank.get_position(), coord)
        (dx, dy, dz) = ((x - coord.q) / d, (y - coord.r) / d, (z - coord.s) / d)
        for i in range(tank.get_max_range()):
            new_hex = Hex(x - (i + 1) * dx, y - (i + 1) * dy, z - (i + 1) * dz)
            if new_hex in shoot_coords:
                for t in enemy_tanks:
                    if new_hex == t.get_position():
                        tanks_shot_at.append(self.tank_from_hex(new_hex))

        return Hex(x - dx, y - dy, z - dz), tanks_shot_at

    def __shoot_coords(self, tank: Tank) -> [Hex]:
        # coords based on center of map
        general_shoot_coords = []
        for radius in range(tank.get_min_range(), tank.get_max_range() + 1):
            general_shoot_coords += self.hexRing(Hex(0, 0, 0), radius)

        # if at_spg keep only straight lines
        if tank.get_type() == "at_spg":
            general_shoot_coords = [coord for coord in general_shoot_coords if 0 in coord]

        # get positional coord based on current tank position and remove those that are not in map
        x, y, z = tank.get_position()
        positional_shoot_coords = [Hex(x + dx, y + dy, z + dz) for (dx, dy, dz) in general_shoot_coords
                                   if not self.__offTheGridDetection(Hex(x + dx, y + dy, z + dz))]

        return positional_shoot_coords

    def neutrality_check(self, tank_1: Tank, tank_2: Tank) -> bool:
        id1, id2 = tank_1.get_player_id(), tank_2.get_player_id()
        id3 = self.third_player(id1, id2)
        if id1 in self.__shoot_actions[id2] or id2 not in self.__shoot_actions[id3]:
            return False
        else:
            return True

    def third_player(self, id1: int, id2: int) -> int:
        for idx in self.__player_ids:
            if idx != id1 and idx != id2:
                return idx

    @staticmethod
    def distance(h1: Hex, h2: Hex) -> int:
        return int((abs(h1.q - h2.q) + abs(h1.r - h2.r) + abs(h1.s - h2.s)) / 2)

    def is_in_base(self, tank_pos: Hex) -> bool:
        return tank_pos in self.__base

    @staticmethod
    def fromDictToHex(data: dict) -> Hex:
        return Hex(data['x'], data['y'], data['z'])

    @staticmethod
    def __hexDirection(direction) -> Hex:
        return Map.hexDirectionVectors[direction]

    @staticmethod
    def __hexAdd(h, vector) -> Hex:
        return Hex(h.q + vector.q, h.r + vector.r, h.s + vector.s)

    def __hexNeighbor(self, h, direction) -> Hex:
        return self.__hexAdd(h, self.__hexDirection(direction))

    def __hexNeighbors(self, h: Hex) -> [Hex]:
        neighbors = []
        for direction in range(6):
            new_neighbor = self.__hexNeighbor(h, direction)
            if not self.__offTheGridDetection(new_neighbor):
                neighbors.append(new_neighbor)

        return neighbors

    @staticmethod
    def __hexScale(h, factor) -> Hex:
        return Hex(h.q * factor, h.r * factor, h.s * factor)

    # Returns a list of a hexes that are in a ring on certain radius
    def hexRing(self, center, radius) -> [Hex]:
        results = []
        h = Map.__hexAdd(center, Map.__hexScale(Map.__hexDirection(4), radius))
        for i in range(6):
            for j in range(radius):
                results.append(h)
                h = self.__hexNeighbor(h, i)

        return results

    # Returns a list of hexes that are in a spiral on certain radius
    def __hexSpiral(self, center, radius) -> [Hex]:
        results = [center]
        for k in range(radius):
            results += self.hexRing(center, k)

        return results

    # Definition of function that converts pixel coordinates to cubic
    @staticmethod
    def __pixelToHex(x, y) -> Hex:
        r = 2 * x / Map.HEX_SIZE / 3
        q = y / Map.HEX_SIZE / math.sqrt(3) - r / 2
        s = -q - r

        return Hex(q, r, s)

    # Definition of function that converts cubic coordinates to pixel coordinates
    @staticmethod
    def hexToPixel(q, r) -> tuple:
        screen_x = Map.HEX_SIZE * 3 / 2 * r
        screen_y = Map.HEX_SIZE * math.sqrt(3) * (q + r / 2)

        return int(screen_x + Map.WIDTH / 2), int(screen_y + Map.HEIGHT / 2)

    # Detects if the given coordinate is off the grid
    def __offTheGridDetection(self, h: Hex) -> bool:
        if h in self.__map:
            return False

        return True
