import pygame
from pygame import Surface
from pygame.time import Clock

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, ICON_PATH
from src.gui.menu import Menu


class Controller:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Game Wizards")
        pygame.display.set_icon(pygame.image.load(ICON_PATH))
        self.__background_music = pygame.mixer.Sound("src/assets/sounds/background_music.mp3")
        self.__background_music.set_volume(0.05)
        self.__background_music.play(100)

        self.__music: bool = False
        self.__running: bool = True
        self.__playing: bool = False
        self.__game = None

        self.__screen: Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.__clock: Clock = Clock()

        self.__menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, self.start_game)

    def start_game(self, game) -> None:
        self.__menu.disable()
        self.__music = False
        self.__game = game

        self.__playing = True
        self.__game.start()

        while not self.__game.map:
            pass

    def __events(self) -> list[pygame.event.Event]:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.__game:
                    self.__game.running = False
                self.__playing = False
                self.__running = False

        return events

    def start_controller(self) -> None:
        try:
            self.run()
        finally:
            if self.__game:
                self.__game.running = False
            pygame.quit()

    def run(self) -> None:
        while self.__running:

            events = self.__events()

            if self.__menu.is_enabled():
                self.__menu.update(events)
                self.__menu.draw(self.__screen)

            if self.__menu.is_end_screen_enabled():
                self.__menu.update_end_screen(events)
                self.__menu.draw_end_screen(self.__screen)

            if self.__playing and self.__game.running:
                self.__game.map.draw_map(self.__screen, self.__game.current_turn, self.__game.num_turns,
                                         self.__game.current_round, self.__game.num_rounds)

            if self.__playing and not self.__game.running:
                print("Game is over!")
                self.__playing = False
                self.__menu.disable()
                self.__menu.enable_end_screen()

            self.__clock.tick(60)
            pygame.display.flip()
