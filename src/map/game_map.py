import pygame
from pygame import Surface
from pygame.font import Font
import random
from typing import Any, Optional

from src.map.hex import Hex
from src.vehicles.tank import Tank
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, BASE_COLOR, OBSTACLE_COLOR, HP_COLOR, RED


class Map:
    def __init__(self, game_map: dict, game_state: dict, players_in_game: dict) -> None:
        pygame.init()
        self.screen: Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game Wizards")
        self.__font_size: int = 24
        self.__font: Font = pygame.font.Font(None, self.__font_size)

        self.__map: list[Hex] = []
        self.__tanks: dict[int, Tank] = {}
        self.__tank_positions: dict[int, Hex] = {}
        self.__spawn_points: list[Hex] = []

        self.__base: list[Hex] = []
        self.__obstacles: list[Hex] = []
        self.__light_repair: list[Hex] = []
        self.__heavy_repair: list[Hex] = []
        self.__catapult: dict[Hex, int] = {}

        self.__shoot_actions: dict[int, []] = {}
        self.__player_ids: list[int] = []
        self.__initialize_map(game_map, game_state, players_in_game)

    def __initialize_map(self, game_map: dict, game_state: dict, players_in_game: dict) -> None:
        self.__map = Hex.hex_spiral(Hex(0, 0, 0), game_map["size"])

        for idx, player in players_in_game.items():
            if not player.is_observer:
                self.__player_ids.append(idx)

        for idx in self.__player_ids:
            self.__shoot_actions[idx] = []

        for tank_id, tank_info in game_state["vehicles"].items():
            player = players_in_game[tank_info["player_id"]]
            tank = Tank(int(tank_id), tank_info, player.tank_color, player.spawn_color)
            self.__tanks[int(tank_id)] = tank
            player.add_tank(tank)
            self.__spawn_points.append(Hex.dict_to_hex(tank_info["spawn_position"]))

        for player in players_in_game.values():
            if not player.is_observer:
                player.reorder()

        for h, positions in game_map["content"].items():
            for position in positions:
                new_hex = Hex.dict_to_hex(position)
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

    def draw(self, current_turn: int, num_turns: int) -> None:
        self.__draw_map()
        self.__draw_turn_number(current_turn, num_turns)

        self.__draw_base()
        self.__draw_obstacles()

        self.__draw_special(list(self.__catapult.keys()), "catapult")
        self.__draw_special(self.__heavy_repair, "heavy_repair")
        self.__draw_special(self.__light_repair, "light_repair")

        self.__draw_tanks_and_spawns()
        self.__draw_hp()

        self.__draw_legend()

        pygame.display.flip()

    def update_map(self, game_state: dict) -> None:
        for tank_id, tank_info in game_state["vehicles"].items():
            tank_id = int(tank_id)
            self.__tank_positions[tank_id] = Hex.dict_to_hex(tank_info["position"])
            server_position = Hex.dict_to_hex(tank_info["position"])
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

    def __draw_map(self) -> None:
        self.screen.fill(WHITE)
        for h in self.__map:
            points = Hex.get_center(h)
            pygame.draw.polygon(self.screen, BLACK, points, 3)

    def __draw_turn_number(self, current_turn: int, num_turns: int):
        text = self.__font.render(f"TURN NUMBER: {current_turn + 1}/{num_turns}", True, BLACK)
        self.screen.blit(text, (30, 25))

    def __draw_base(self) -> None:
        for h in self.__base:
            self.__color_hex(h, BASE_COLOR)

    def __draw_obstacles(self) -> None:
        for h in self.__obstacles:
            self.__color_hex(h, OBSTACLE_COLOR)

    def __draw_special(self, hexes: list[Hex], name: str) -> None:
        image = pygame.image.load(f"src/assets/special_hexes/{name}.png")
        scaled_image = pygame.transform.scale(image, (28, 28))
        for h in hexes:
            x, y = Hex.hex_to_pixel(h.q, h.r)
            self.screen.blit(scaled_image, (x - 14, y - 14))

    def __draw_tanks_and_spawns(self) -> None:
        for tank in self.__tanks.values():
            self.__color_hex(tank.get_spawn_position(), tank.spawn_color)
            self.__draw_tank(tank)

    def __draw_tank(self, tank: Tank) -> None:
        image = pygame.image.load(f"src/assets/vehicle_types/{tank.get_type()}.png")
        scaled_image = pygame.transform.scale(image, (28, 28))
        h = tank.get_position()
        color = pygame.Surface(scaled_image.get_size())
        color.fill(tank.tank_color)
        scaled_image.blit(color, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        x, y = Hex.hex_to_pixel(h.q, h.r)
        self.screen.blit(scaled_image, (x - 14, y - 14))

    def __color_hex(self, h: Hex, color: tuple) -> None:
        points = Hex.get_center(h)
        pygame.draw.polygon(self.screen, color, points, 0)
        pygame.draw.polygon(self.screen, BLACK, points, 3)

    def __draw_hp(self) -> None:
        for tank in self.__tanks.values():
            ratio_green = tank.get_hp() * 1.0 / tank.get_full_hp()
            q, r = tank.get_position().q, tank.get_position().r
            x, y = Hex.hex_to_pixel(q, r)
            x, y = x - 9, y - 13
            line_start_g = (x, y)
            line_end_g = (x + 18 * ratio_green, y)
            line_start_r = (x + 18 * ratio_green + 1, y)
            line_end_r = (x + 18, y)
            pygame.draw.line(self.screen, HP_COLOR, line_start_g, line_end_g, 4)
            if ratio_green != 1.0:
                pygame.draw.line(self.screen, RED, line_start_r, line_end_r, 4)

    def __draw_legend(self) -> None:
        pass

    def draw_shoot_animation(self, tank: Tank, tanks: list[Tank]) -> None:
        h1 = tank.get_position()
        for t in tanks:
            h2 = t.get_position()
            x1, y1 = Hex.hex_to_pixel(h1.q, h1.r)
            x2, y2 = Hex.hex_to_pixel(h2.q, h2.r)
            points = Hex.get_center(h2)
            pygame.draw.polygon(self.screen, RED, points, 3)
            pygame.draw.line(self.screen, RED, (x1, y1), (x2, y2), 5)

        pygame.display.flip()

    def draw_attacked_hp(self, tanks: list[Tank], damage: int) -> None:
        for t in tanks:
            new_hp = t.get_hp() - damage
            if new_hp < 0:
                new_hp = 0
            ratio_green = new_hp * 1.0 / t.get_full_hp()
            q, r = t.get_position().q, t.get_position().r
            x, y = Hex.hex_to_pixel(q, r)
            x, y = x - 9, y - 13
            line_start_g = (x, y)
            line_end_g = (x + 18 * ratio_green, y)
            line_start_r = (x + 18 * ratio_green + 1, y)
            line_end_r = (x + 18, y)
            if ratio_green != 0:
                pygame.draw.line(self.screen, HP_COLOR, line_start_g, line_end_g, 4)
            elif ratio_green == 0:
                line_start_r = line_start_g
            pygame.draw.line(self.screen, RED, line_start_r, line_end_r, 4)

        pygame.display.flip()

    def move(self, start: Hex, movement: int) -> Hex:
        visited = []
        rings = [[start]]
        for k in range(1, movement + 1):
            rings.append([])
            for h in rings[k - 1]:
                for direction in range(6):
                    neighbor = Hex.hex_neighbor(h, direction)
                    if neighbor not in visited and neighbor not in self.__obstacles \
                            and not self.__offTheGridDetection(neighbor):
                        visited.append(neighbor)
                        rings[k].append(neighbor)

        visited = [h for h in visited if h not in self.__spawn_points and h not in self.__tank_positions.values()]
        visited.sort(key=lambda x: x)

        move_to = []
        if visited:
            d = Hex.distance(Hex(0, 0, 0), visited[0])
            move_to = [h for h in visited if Hex.distance(Hex(0, 0, 0), h) == d]

        return random.choice(move_to) if visited else None

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

    def shoot(self, tank: Tank) -> tuple[Optional[Hex], Optional[list[Tank]]]:
        if tank.get_type() != "at_spg":
            return self.__curved_trajectory(tank)
        else:
            return self.__straight_trajectory(tank)

    def __curved_trajectory(self, tank: Tank) -> tuple[Optional[Hex], Optional[list[Tank]]]:
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
            if t.get_player_id() == tank.get_player_id() or self.__neutrality_check(tank, t):
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
        tank_shoot_coords = [self.__tank_from_hex(h) for h in shoot_coords]

        # Keep tanks whose hp is > 0 and sort them based on hp
        tank_shoot_coords = [t for t in tank_shoot_coords if t.get_hp() > 0]
        tank_shoot_coords.sort(key=lambda tt: tt)

        # Shoot at tank with the lowest hp
        if tank_shoot_coords:
            return tank_shoot_coords[0].get_position(), [tank_shoot_coords[0]]
        else:
            return None, None

    def __straight_trajectory(self, tank: Tank) -> tuple[Optional[Hex], Optional[list[Tank]]]:
        # Shoot coords based on tank position
        shoot_coords = self.__shoot_coords(tank)
        x, y, z = tank.get_position()

        # Blocked hexes
        blocked = []

        # Add obstacles to blocked
        for coord in shoot_coords:
            if coord in self.__obstacles:
                blocked.append(coord)
                d = Hex.distance(tank.get_position(), coord)
                (dx, dy, dz) = ((x - coord.q) / d, (y - coord.r) / d, (z - coord.s) / d)
                for i in range(tank.get_max_range() - d):
                    blocked.append(Hex(coord.q - (i + 1) * dx, coord.r - (i + 1) * dy, coord.s - (i + 1) * dz))

        # Add to blocked my tanks that are not in 1st ring and neutral (if in 1st ring add whole line)
        for t in self.__tanks.values():
            coord = t.get_position()
            if t.get_player_id() == tank.get_player_id() and Hex.distance(coord, tank.get_position()) > 1:
                blocked.append(coord)
            elif self.__neutrality_check(tank, t):
                if Hex.distance(coord, tank.get_position()) == 1:
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
            if t.get_player_id() != tank.get_player_id() and not self.__neutrality_check(tank, t):
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
        d = Hex.distance(tank.get_position(), coord)
        (dx, dy, dz) = ((x - coord.q) / d, (y - coord.r) / d, (z - coord.s) / d)
        for i in range(tank.get_max_range()):
            new_hex = Hex(x - (i + 1) * dx, y - (i + 1) * dy, z - (i + 1) * dz)
            if new_hex in shoot_coords:
                for t in enemy_tanks:
                    if new_hex == t.get_position():
                        tanks_shot_at.append(self.__tank_from_hex(new_hex))

        return Hex(x - dx, y - dy, z - dz), tanks_shot_at

    def __shoot_coords(self, tank: Tank) -> list[Hex]:
        # coords based on center of map
        general_shoot_coords = []
        for radius in range(tank.get_min_range(), tank.get_max_range() + 1):
            general_shoot_coords += Hex.hex_ring(Hex(0, 0, 0), radius)

        # if at_spg keep only straight lines
        if tank.get_type() == "at_spg":
            general_shoot_coords = [coord for coord in general_shoot_coords if 0 in coord]

        # get positional coord based on current tank position and remove those that are not in map
        x, y, z = tank.get_position()
        positional_shoot_coords = [Hex(x + dx, y + dy, z + dz) for (dx, dy, dz) in general_shoot_coords
                                   if not self.__offTheGridDetection(Hex(x + dx, y + dy, z + dz))]

        return positional_shoot_coords

    def __tank_from_hex(self, h: Hex) -> Tank:
        return self.__tanks[Map.__get_key_from_value(self.__tank_positions, h)[0]]

    @staticmethod
    def __get_key_from_value(d: dict, value: Any) -> list[Any]:
        return [k for k, v in d.items() if v == value]

    def __neutrality_check(self, tank_1: Tank, tank_2: Tank) -> bool:
        id1, id2 = tank_1.get_player_id(), tank_2.get_player_id()
        id3 = self.__third_player(id1, id2)
        if id1 in self.__shoot_actions[id2] or id2 not in self.__shoot_actions[id3]:
            return False
        else:
            return True

    def __third_player(self, id1: int, id2: int) -> int:
        for idx in self.__player_ids:
            if idx != id1 and idx != id2:
                return idx

    def reset_shoot_actions(self, player_id: int) -> None:
        self.__shoot_actions[player_id] = []

    def is_in_base(self, tank_pos: Hex) -> bool:
        return tank_pos in self.__base

    # Detects if the given coordinate is off the grid
    def __offTheGridDetection(self, h: Hex) -> bool:
        if h in self.__map:
            return False

        return True
