import pygame
from pygame import Surface
from pygame.font import Font

from src.map.hex import Hex
from src.vehicles.tank import Tank
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, BASE_COLOR, OBSTACLE_COLOR, HP_COLOR, RED


class Painter:
    def __init__(self, map: dict, players: list):
        pygame.init()
        self.screen: Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game Wizards")
        self.__font_size: int = 24
        self.__font: Font = pygame.font.Font(None, self.__font_size)
        self.__map: dict[Hex, dict] = map
        self.__players: list = players

        self.__tanks: dict[int, Tank] = {d["tank"].get_id(): d["tank"]
                                         for d in self.__map.values() if d["tank"] is not None}

    def draw(self, current_turn: int, num_turns: int) -> None:
        self.__draw_map()
        self.__draw_turn_number(current_turn, num_turns)
        self.__draw_scoreboard()

        for hex, characteristics in self.__map.items():
            if characteristics["type"] == "base":
                self.__draw_base(hex)
            elif characteristics["type"] == "obstacle":
                self.__draw_obstacles(hex)
            elif characteristics["type"] == "catapult":
                self.__draw_special(hex, "catapult")
            elif characteristics["type"] == "heavy_repair":
                self.__draw_special(hex, "heavy_repair")
            elif characteristics["type"] == "light_repair":
                self.__draw_special(hex, "light_repair")

        self.__draw_tanks_and_spawns()
        self.__draw_hp()

        self.__draw_legend()

        pygame.display.flip()

    def __draw_map(self) -> None:
        self.screen.fill(WHITE)
        for h in self.__map.keys():
            points = Hex.get_center(h)
            pygame.draw.polygon(self.screen, BLACK, points, 3)

    def __draw_turn_number(self, current_turn: int, num_turns: int):
        text = self.__font.render(f"TURN NUMBER: {current_turn + 1}/{num_turns}", True, BLACK)
        self.screen.blit(text, (30, 25))

    def __draw_base(self, h: Hex) -> None:
        self.__color_hex(h, BASE_COLOR)

    def __draw_obstacles(self, h: Hex) -> None:
        self.__color_hex(h, OBSTACLE_COLOR)

    def __draw_special(self, h: Hex, name: str) -> None:
        image = pygame.image.load(f"src/assets/special_hexes/{name}.png")
        scaled_image = pygame.transform.scale(image, (28, 28))
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

    def __draw_scoreboard(self) -> None:

        text = self.__font.render("CAPTURE POINTS", True, BLACK)
        self.screen.blit(text, (50, 200))

        starting_coords = (30, 250)
        starting_coords2 = (30, 530)
        for index, player in enumerate(self.__players):
            text = self.__font.render(f"{player.name}       {player.get_capture_points()}", True, BLACK)
            self.screen.blit(text, (starting_coords[0], starting_coords[1] + index * 30))

        pygame.draw.line(self.screen, BLACK, (30, 400), (250, 400), 5)

        text = self.__font.render("DESTRUCTION POINTS", True, BLACK)
        self.screen.blit(text, (50, 480))

        for index, player in enumerate(self.__players):
            text = self.__font.render(f"{player.name}       {player.get_destruction_points()}", True, BLACK)
            self.screen.blit(text, (starting_coords2[0], starting_coords2[1] + index * 30))

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
