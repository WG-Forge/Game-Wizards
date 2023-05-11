import pygame
from pygame import Surface
from pygame.font import Font

from src.map.hex import Hex
from src.vehicles.tank import Tank
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, BASE_COLOR, OBSTACLE_COLOR, HP_COLOR, RED, \
    LEGEND_ORDER, LEGEND_POSITIONS, LEGEND_TEXT, LEGEND_TEXT_POSITION, LEGEND_NAME, BACKGROUND_PATH


class Painter:
    def __init__(self, game_map: dict, players: list):
        pygame.init()
        pygame.display.set_caption("Game Wizards")
        pygame.display.set_icon(pygame.image.load("src/assets/screen/icon.png"))
        self.screen: Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__font_size: int = 21
        self.__font: Font = pygame.font.Font("src/assets/screen/BF_Modernista-Regular.ttf", self.__font_size)
        self.__map: dict[Hex, dict] = game_map
        self.__players: list = players

        self.__tanks: dict[int, Tank] = {d["tank"].get_id(): d["tank"]
                                         for d in self.__map.values() if d["tank"] is not None}
        self.__images: dict[str, Surface] = {}
        self.__load_images()

    def __load_images(self) -> None:
        self.__images: dict = {
            "spg": Painter.__load_image(LEGEND_ORDER[0]),
            "light_tank": Painter.__load_image(LEGEND_ORDER[1]),
            "heavy_tank": Painter.__load_image(LEGEND_ORDER[2]),
            "medium_tank": Painter.__load_image(LEGEND_ORDER[3]),
            "at_spg": Painter.__load_image(LEGEND_ORDER[4]),
            "catapult": Painter.__load_image(LEGEND_ORDER[5]),
            "heavy_repair": Painter.__load_image(LEGEND_ORDER[6]),
            "light_repair": Painter.__load_image(LEGEND_ORDER[7])
        }

    @staticmethod
    def __load_image(img_path: str) -> Surface:
        return pygame.image.load(img_path).convert_alpha()

    def draw(self, current_turn: int, num_turns: int, current_round: int, num_rounds: int) -> None:
        self.__draw_map()
        self.__draw_turn_and_round(current_turn, num_turns, current_round, num_rounds)
        self.__draw_scoreboard()

        for h, characteristics in self.__map.items():
            if characteristics["type"] == "base":
                self.__draw_base(h)
            elif characteristics["type"] == "obstacle":
                self.__draw_obstacles(h)
            elif characteristics["type"] == "catapult":
                self.__draw_special(h, "catapult")
            elif characteristics["type"] == "heavy_repair":
                self.__draw_special(h, "heavy_repair")
            elif characteristics["type"] == "light_repair":
                self.__draw_special(h, "light_repair")

        self.__draw_tanks_and_spawns()
        self.__draw_hp()

        self.__draw_legend()

        pygame.display.flip()

    def __draw_map(self) -> None:
        image = pygame.transform.scale(pygame.image.load(BACKGROUND_PATH), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(image, (0, 0))
        for h in self.__map.keys():
            self.__color_hex(h, WHITE)

    def __draw_turn_and_round(self, current_turn: int, num_turns: int, current_round: int, num_rounds: int):
        text = self.__font.render(f"TURN: {current_turn}/{num_turns}", True, BLACK)
        self.screen.blit(text, (400, 25))
        text = self.__font.render(f"ROUND: {current_round}/{num_rounds}", True, BLACK)
        self.screen.blit(text, (700, 25))

    def __draw_base(self, h: Hex) -> None:
        self.__color_hex(h, BASE_COLOR)

    def __draw_obstacles(self, h: Hex) -> None:
        self.__color_hex(h, OBSTACLE_COLOR)

    def __draw_special(self, h: Hex, name: str) -> None:
        image = self.__images[name]
        scaled_image = pygame.transform.scale(image, (28, 28))
        x, y = Hex.hex_to_pixel(h.q, h.r)
        self.screen.blit(scaled_image, (x - 14, y - 14))

    def __draw_tanks_and_spawns(self) -> None:
        for tank in self.__tanks.values():
            self.__color_hex(tank.get_spawn_position(), tank.spawn_color)
            self.__draw_tank(tank)

    def __draw_tank(self, tank: Tank = None) -> None:
        image = self.__images[tank.get_type()]
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
        for i in range(8):
            h = Hex(t=LEGEND_POSITIONS[i])
            self.__color_hex(h, OBSTACLE_COLOR)
            scaled_image = pygame.transform.scale(self.__images[LEGEND_NAME[i]], (28, 28))
            x, y = Hex.hex_to_pixel(h.q, h.r)
            self.screen.blit(scaled_image, (x - 14, y - 14))
            text = self.__font.render(LEGEND_TEXT[i], True, BLACK)
            self.screen.blit(text, LEGEND_TEXT_POSITION[i])

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
