import pygame
from pygame import Surface
import pygame_menu
from pygame_menu import sound
from pygame_menu.locals import ALIGN_CENTER, POSITION_SOUTH, ALIGN_LEFT, ALIGN_RIGHT

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_FONT_SIZE, BUTTON_MARGIN, TITLE_SIZE, TRANSPARENT_COLOR, \
    MAIN_FRAME_WIDTH, SECTIONS_COLOR, MAIN_FRAME_HEIGHT, LABEL_SIZE, MAX_INPUT_CHARS, PACKING_MARGIN, SECTION_WIDTH
from src.gui.theme import load_default_theme, random_background
from src.game_types.local_game import local_game
from src.game_types.online_game import online_game


class Menu:
    def __init__(self, width: int, height: int, start_game):
        self.__screen_width: int = width
        self.__screen_height: int = height
        self.__start_game = start_game

        self.__theme = load_default_theme()
        self.__create_menus()
        engine = sound.Sound()
        engine.set_sound(sound.SOUND_TYPE_CLICK_MOUSE, "src/assets/sounds/button_click.wav", volume=0.2)
        engine.set_sound(sound.SOUND_TYPE_WIDGET_SELECTION, "src/assets/sounds/button_hover.wav", volume=1.0)
        self.__main_menu.set_sound(engine, True)
        self.__end_screen.set_sound(engine, True)
        self.__end_screen.disable()

    def __create_menus(self) -> None:
        self.__create_options_menu()
        self.__create_about_menu()
        self.__create_join_game_menu()
        self.__create_local_multiplayer_game_menu()
        self.__create_main_menu()
        self.__create_end_screen()

    def __create_main_menu(self) -> None:
        self.__main_menu = pygame_menu.Menu("Main Menu", SCREEN_WIDTH, SCREEN_HEIGHT, theme=self.__theme,
                                            mouse_motion_selection=True)
        self.__theme.background_color = random_background()
        self.__main_menu.add.button("Online Game", self.__join_menu, font_size=BUTTON_FONT_SIZE,
                                    margin=BUTTON_MARGIN)
        self.__main_menu.add.button("Local Game", self.__local_multiplayer_menu,
                                    font_size=BUTTON_FONT_SIZE,
                                    margin=BUTTON_MARGIN)
        self.__main_menu.add.button("About/Credits", self.about_menu, font_size=BUTTON_FONT_SIZE,
                                    margin=BUTTON_MARGIN)
        self.__main_menu.add.button("Quit", pygame_menu.events.EXIT, font_size=BUTTON_FONT_SIZE,
                                    margin=BUTTON_MARGIN)

    def __create_loading_menu(self) -> None:
        self.__loading_menu = pygame_menu.Menu("Loading", SCREEN_WIDTH, SCREEN_HEIGHT, theme=self.__theme,
                                               mouse_motion_selection=True)
        self.__theme.background_color = random_background()
        self.loading_message = self.__loading_menu.add.label("Loading...", font_size=TITLE_SIZE,
                                                             margin=BUTTON_MARGIN, align=ALIGN_CENTER)

    def __create_options_menu(self) -> None:
        self.__options_menu = pygame_menu.Menu("Options", SCREEN_WIDTH, SCREEN_HEIGHT, theme=self.__theme,
                                               mouse_motion_selection=True)
        self.__theme.background_color = random_background()
        self.back = self.__options_menu.add.button("Back", pygame_menu.events.BACK, font_size=BUTTON_FONT_SIZE,
                                                   margin=BUTTON_MARGIN)

    def __create_about_menu(self) -> None:
        self.about_menu = pygame_menu.Menu("About/Credits", SCREEN_WIDTH, SCREEN_HEIGHT, theme=self.__theme,
                                           mouse_motion_selection=True)
        self.__theme.background_color = random_background()
        self.created_by = self.about_menu.add.label("Created by Game-Wizards", font_size=BUTTON_FONT_SIZE,
                                                    margin=PACKING_MARGIN)
        self.authors = self.about_menu.add.label("Authors:", align=ALIGN_CENTER, margin=PACKING_MARGIN,
                                                 font_size=TITLE_SIZE+5)
        self.author1 = self.about_menu.add.label("Veljko", align=ALIGN_CENTER, margin=PACKING_MARGIN,
                                                 font_size=TITLE_SIZE)
        self.author2 = self.about_menu.add.label("Željko", align=ALIGN_CENTER, margin=PACKING_MARGIN,
                                                 font_size=TITLE_SIZE)
        self.author3 = self.about_menu.add.label("Olegas", align=ALIGN_CENTER, margin=PACKING_MARGIN,
                                                 font_size=TITLE_SIZE)

        self.created_by.set_alignment(pygame_menu.locals.ALIGN_CENTER)

        self.version = self.about_menu.add.label("Version 1.0")
        self.version.set_border(0, TRANSPARENT_COLOR)
        self.version._background_color = TRANSPARENT_COLOR
        self.version.update_font({'color': (255, 255, 255)})
        self.version.update_font({'size': 14})
        self.version.set_alignment(pygame_menu.locals.ALIGN_CENTER)
        self.version.translate(0, 250)

        self.back = self.about_menu.add.button("Back", pygame_menu.events.BACK, font_size=BUTTON_FONT_SIZE,
                                               margin=BUTTON_MARGIN)
        self.back.translate(0, 150)

    def __create_end_screen(self) -> None:
        self.__end_screen = pygame_menu.Menu("Game end", SCREEN_WIDTH, SCREEN_HEIGHT, theme=self.__theme,
                                             mouse_motion_selection=True)
        self.__theme.background_color = random_background()
        self.__end_screen.add.button("Play again", self.functions, font_size=BUTTON_FONT_SIZE,
                                     margin=BUTTON_MARGIN)
        self.__end_screen.add.button("Quit", pygame_menu.events.EXIT, font_size=BUTTON_FONT_SIZE,
                                     margin=BUTTON_MARGIN)

    def __create_join_game_menu(self) -> None:
        self.__join_menu = pygame_menu.Menu("Join Game", SCREEN_WIDTH, SCREEN_HEIGHT, theme=self.__theme,
                                            mouse_motion_selection=True)
        self.__theme.background_color = random_background()

        self.join_game_frame = self.__join_menu.add.frame_v(MAIN_FRAME_WIDTH, MAIN_FRAME_HEIGHT,
                                                            frame_id="MainJoinGame", background_color=SECTIONS_COLOR,
                                                            align=ALIGN_CENTER)

        # Join game menu elements
        self.join_game_label = self.__join_menu.add.label("Join server", font_size=TITLE_SIZE,
                                                          background_color=TRANSPARENT_COLOR,
                                                          border_color=SECTIONS_COLOR)

        self.game_name_label = self.__join_menu.add.label("Game name", background_color=TRANSPARENT_COLOR,
                                                          border_color=SECTIONS_COLOR, font_size=LABEL_SIZE)
        self.game_name = self.__join_menu.add.text_input("", maxchar=MAX_INPUT_CHARS,
                                                         input_underline='_', textinput_id="game_name_id")

        self.player_name_label = self.__join_menu.add.label("Player   name", background_color=TRANSPARENT_COLOR,
                                                            border_color=SECTIONS_COLOR, font_size=LABEL_SIZE)
        self.player_name = self.__join_menu.add.text_input("", maxchar=MAX_INPUT_CHARS,
                                                           input_underline='_', textinput_id="player_name_id")

        self.join_as_observer = self.__join_menu.add.selector("Join as an observer", [("No", False), ("Yes", True)],
                                                              font_size=LABEL_SIZE,
                                                              selector_id="join_observer_id")

        self.back_button = self.__join_menu.add.button("Back", pygame_menu.events.BACK, font_size=TITLE_SIZE)
        self.start_button = self.__join_menu.add.button("To Battle!", self.__start_online_game,
                                                        font_size=TITLE_SIZE)

        # Advanced tab

        self.advanced_button = self.__join_menu.add.button("Advanced", self.show_advanced_menu,
                                                           font_size=LABEL_SIZE)

        self.player_password_label = self.__join_menu.add.label("Set password", background_color=TRANSPARENT_COLOR,
                                                                border_color=SECTIONS_COLOR,
                                                                font_size=LABEL_SIZE)
        self.player_password = self.__join_menu.add.text_input("", maxchar=MAX_INPUT_CHARS,
                                                               input_underline='_', textinput_id="password_id")

        self.num_turns_label = self.__join_menu.add.label("Number of turns", background_color=TRANSPARENT_COLOR,
                                                          border_color=SECTIONS_COLOR, font_size=LABEL_SIZE)
        self.num_turns = self.__join_menu.add.text_input("", maxchar=3, input_underline='_', default=45,
                                                         textinput_id="turns_number_id")

        self.players_number = self.__join_menu.add.selector("Number of Players: ", [("1 Player", 1),
                                                                                    ("2 Players", 2),
                                                                                    ("3 Players", 3)],
                                                            default=2, font_size=LABEL_SIZE,
                                                            selector_id="players_number_id")

        self.full_game = self.__join_menu.add.selector("Play Full Game: ", [("Yes", True), ("No", False)],
                                                       font_size=LABEL_SIZE, selector_id="full_game_id")

        # Hiding advanced menu elements by default

        self.show_advanced_menu()

        # Advanced frame

        self.advanced_frame = self.__join_menu.add.frame_v(SECTION_WIDTH, 300,
                                                           frame_id="advancedFrame",
                                                           background_color=TRANSPARENT_COLOR,
                                                           border_color=SECTIONS_COLOR)

        self.advanced_frame.pack(self.player_password_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.advanced_frame.pack(self.player_password, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.advanced_frame.pack(self.num_turns_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.advanced_frame.pack(self.num_turns, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.advanced_frame.pack(self.players_number, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.advanced_frame.pack(self.full_game, align=ALIGN_CENTER, margin=PACKING_MARGIN)

        self.back_start_frame = self.__join_menu.add.frame_h(SECTION_WIDTH, 110, background_color=TRANSPARENT_COLOR,
                                                             border_color=SECTIONS_COLOR)
        self.back_start_frame.pack(self.start_button, align=ALIGN_RIGHT, vertical_position=POSITION_SOUTH)
        self.back_start_frame.pack(self.back_button, align=ALIGN_LEFT, vertical_position=POSITION_SOUTH, margin=(-3, 0))

        self.join_game_frame.pack(self.join_game_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.join_game_frame.pack(self.game_name_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.join_game_frame.pack(self.game_name, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.join_game_frame.pack(self.player_name_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.join_game_frame.pack(self.player_name, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.join_game_frame.pack(self.join_as_observer, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.join_game_frame.pack(self.advanced_button, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.join_game_frame.pack(self.advanced_frame, align=ALIGN_CENTER)
        self.join_game_frame.pack(self.back_start_frame, align=ALIGN_CENTER, vertical_position=POSITION_SOUTH)

    def __create_local_multiplayer_game_menu(self) -> None:
        self.players = []
        self.observers = []
        self.__local_multiplayer_menu = pygame_menu.Menu("Local Multiplayer", SCREEN_WIDTH, SCREEN_HEIGHT,
                                                         theme=self.__theme, mouse_motion_selection=True)
        self.__theme.background_color = random_background()

        self.game_setup = self.__local_multiplayer_menu.add.frame_v(MAIN_FRAME_WIDTH, MAIN_FRAME_HEIGHT,
                                                                    frame_id="GameSetup",
                                                                    background_color=SECTIONS_COLOR,
                                                                    align=ALIGN_CENTER)

        # All elements of GAME SETUP frame
        self.game_setup_label = self.__local_multiplayer_menu.add.label("Game setup", font_size=TITLE_SIZE,
                                                                        background_color=TRANSPARENT_COLOR,
                                                                        border_color=SECTIONS_COLOR)

        self.game_name_label = self.__local_multiplayer_menu.add.label("Game name", font_size=LABEL_SIZE,
                                                                       background_color=TRANSPARENT_COLOR,
                                                                       border_color=SECTIONS_COLOR)

        self.game_name_input = self.__local_multiplayer_menu.add.text_input("", maxchar=MAX_INPUT_CHARS,
                                                                            input_underline='_',
                                                                            textinput_id="game_name_input_id")

        self.local_players_number = self.__local_multiplayer_menu.add.selector("Number of Players: ", [("1 Player", 1),
                                                                                                       ("2 Players", 2),
                                                                                                       (
                                                                                                           "3 Players",
                                                                                                           3)],
                                                                               default=2,
                                                                               selector_id="local_players_number_id",
                                                                               font_size=LABEL_SIZE)

        self.local_full_game = self.__local_multiplayer_menu.add.selector("Play Full Game: ",
                                                                          [("Yes", True), ("No", False)],
                                                                          font_size=LABEL_SIZE,
                                                                          selector_id="local_full_game_id")

        self.back_button = self.__local_multiplayer_menu.add.button("Back", pygame_menu.events.BACK,
                                                                    font_size=TITLE_SIZE)

        self.player_name_label = self.__local_multiplayer_menu.add.label("Player name:", font_size=LABEL_SIZE,
                                                                         background_color=TRANSPARENT_COLOR,
                                                                         border_color=SECTIONS_COLOR)
        self.player_name_input = self.__local_multiplayer_menu.add.text_input("", maxchar=MAX_INPUT_CHARS,
                                                                              input_underline='_',
                                                                              textinput_id="player_name_input_id")
        self.player_add_button = self.__local_multiplayer_menu.add.button("Add player", self.add_player,
                                                                          font_size=LABEL_SIZE)

        self.start_button = self.__local_multiplayer_menu.add.button("To Battle!", self.__start_local_game,
                                                                     font_size=TITLE_SIZE)

        self.local_num_turns_label = self.__local_multiplayer_menu.add.label("Number of turns",
                                                                             background_color=TRANSPARENT_COLOR,
                                                                             border_color=SECTIONS_COLOR,
                                                                             font_size=LABEL_SIZE)
        self.local_num_turns = self.__local_multiplayer_menu.add.text_input("", maxchar=3, input_underline='_',
                                                                            default=45,
                                                                            textinput_id="local_turns_number_id")

        self.start_back_frame = self.__local_multiplayer_menu.add.frame_h(SECTION_WIDTH, 110,
                                                                          background_color=TRANSPARENT_COLOR,
                                                                          border_color=SECTIONS_COLOR)

        self.start_back_frame.pack(self.start_button, align=ALIGN_RIGHT, vertical_position=POSITION_SOUTH)
        self.start_back_frame.pack(self.back_button, align=ALIGN_LEFT, vertical_position=POSITION_SOUTH, margin=(-3, 0))

        self.game_setup.pack(self.game_setup_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.game_name_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.game_name_input, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.local_num_turns_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.local_num_turns, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.local_players_number, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.local_full_game, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.player_name_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.player_name_input, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.player_add_button, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        # self.game_setup.pack(self.observer_name_label, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        # self.game_setup.pack(self.observer_name_input, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        # self.game_setup.pack(self.observer_add_button, align=ALIGN_CENTER, margin=PACKING_MARGIN)
        self.game_setup.pack(self.start_back_frame, align=ALIGN_CENTER,
                             vertical_position=POSITION_SOUTH)

    def show_advanced_menu(self) -> None:
        if self.player_password_label.is_visible():
            self.player_password_label.hide()
            self.player_password.hide()
            self.num_turns_label.hide()
            self.num_turns.hide()
            self.players_number.hide()
            self.full_game.hide()
        else:
            self.player_password_label.show()
            self.player_password.show()
            self.num_turns_label.show()
            self.num_turns.show()
            self.players_number.show()
            self.full_game.show()

    def __start_local_game(self) -> None:
        self.__start_game(local_game(self.__local_multiplayer_menu.get_widget("game_name_input_id").get_value(),
                                     self.players, self.observers, self.__local_multiplayer_menu.get_widget(
                "local_players_number_id").get_value()[0][1], self.__local_multiplayer_menu.get_widget(
                "local_turns_number_id").get_value(), self.__local_multiplayer_menu.get_widget(
                "local_full_game_id").get_value()[0][1]))
        self.__local_multiplayer_menu.get_widget("game_name_input_id").set_value("")
        self.players = []
        self.observers = []

    def __start_online_game(self) -> None:
        self.__start_game(online_game(self.__join_menu.get_widget("game_name_id").get_value(),
                                      self.__join_menu.get_widget("player_name_id").get_value(),
                                      self.__join_menu.get_widget("players_number_id").get_value()[0][1],
                                      self.__join_menu.get_widget("turns_number_id").get_value(),
                                      self.__join_menu.get_widget("full_game_id").get_value()[0][1],
                                      self.__join_menu.get_widget("password_id").get_value(),
                                      self.__join_menu.get_widget("join_observer_id").get_value()[0][1]))
        self.__join_menu.get_widget("game_name_id").set_value("")
        self.__join_menu.get_widget("player_name_id").set_value("")
        self.__join_menu.get_widget("password_id").set_value("")

    def add_player(self) -> None:
        self.players.append(self.__local_multiplayer_menu.get_widget("player_name_input_id").get_value())
        self.__local_multiplayer_menu.get_widget("player_name_input_id").set_value("")

    def functions(self) -> None:
        self.enable()
        self.disable_end_screen()

    def is_enabled(self) -> bool:
        return self.__main_menu.is_enabled()

    def is_end_screen_enabled(self) -> bool:
        return self.__end_screen.is_enabled()

    def draw(self, screen: Surface) -> None:
        if self.__main_menu.is_enabled():
            self.__main_menu.draw(screen)

    def draw_end_screen(self, screen: Surface) -> None:
        if self.__end_screen.is_enabled():
            self.__end_screen.draw(screen)

    def update(self, events: list[pygame.event.Event]) -> None:
        self.__main_menu.update(events)

    def update_end_screen(self, events: list[pygame.event.Event]) -> None:
        self.__end_screen.update(events)

    def disable(self) -> None:
        self.__main_menu.disable()

    def disable_end_screen(self) -> None:
        self.__end_screen.disable()

    def enable(self) -> None:
        self.__main_menu.enable()

    def enable_end_screen(self) -> None:
        self.__end_screen.enable()
