import pygame
from pygame.time import Clock
from threading import Semaphore
from typing import Optional

from src.client.game_client import Client
from src.map.game_map import Map
from src.players.player_factory import PlayerFactory
from src.players.player import Player


class Game:
    def __init__(self, name: str = None, max_players: int = 1, num_turns: int = None, is_full: bool = False) -> None:
        self.__name: str = name
        self.__map: Optional[Map] = None
        self.__running: bool = False
        self.__winner: Optional[int] = None
        self.__is_full: bool = is_full

        self.__num_turns: int = num_turns
        self.__current_turn: Optional[int] = None
        self.__num_rounds: Optional[int] = None
        self.__current_round: Optional[int] = None

        self.__current_client: Client = Client()
        self.__all_clients: dict[Player, Client] = {}

        self.__current_player: Optional[Player] = None
        self.__waiting_players: list[Player] = []
        self.__players_in_game: dict[int, Player] = {}

        self.__current_player_idx: Optional[int] = None
        self.__max_players: int = max_players
        self.__game_players: int = 0
        self.__all_players: int = 0

        self.__turn_played_sem: Semaphore = Semaphore(0)
        self.__clock: Clock = Clock()

    def add_player(self, name: str, password: str = None, is_observer: bool = None) -> None:
        if self.__game_players >= self.__max_players:
            is_observer = True

        if not is_observer:
            self.__game_players += 1

        self.__all_players += 1

        player: Player
        player_type: str

        if is_observer:
            player_type = "observer"
        else:
            player_type = "bot_player"

        player = PlayerFactory.create_player(player_type, name, self.__turn_played_sem, self.__current_player_idx,
                                             self.__game_players-1, password, is_observer)

        self.__waiting_players.append(player)

    def start_game(self) -> None:
        if not self.__waiting_players:
            raise RuntimeError("Can't start the game without any players!")

        self.__running = True
        for p in self.__waiting_players:
            self.__connect(p)

        self.run()

    def run(self) -> None:
        self.__initialize_game()

        while self.__running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__running = False

            self.__map.draw(self.__current_turn, self.__num_turns)

            self.__clock.tick(30)

            for player in self.__players_in_game.values():
                player.next_turn_sem.release()

            for _ in range(self.__all_players):
                self.__turn_played_sem.acquire()

            self.__update_game(self.__current_client.game_state())

        self.__end_game()

    def __update_game(self, game_state: dict) -> None:
        self.__current_turn = game_state["current_turn"]
        if game_state["finished"] or self.__current_turn == self.__num_turns:
            self.__running = False
            self.__winner = game_state["winner"]
            return

        self.__current_player_idx = game_state["current_player_idx"]
        self.__current_player = self.__players_in_game[self.__current_player_idx]
        self.__current_client = self.__all_clients[self.__current_player]

        for p in self.__players_in_game.values():
            p.set_curr(self.__current_player_idx)

        print()
        print(f"Current turn: {self.__current_turn}, "
              f"current player: {self.__current_player.name}")

        self.__map.update_map(game_state)

    def __initialize_game(self) -> None:
        game_map: dict = self.__current_client.map()
        game_state: dict = self.__current_client.game_state()

        self.__max_players = game_state["num_players"]
        self.__num_turns = game_state["num_turns"]
        self.__num_rounds = game_state["num_rounds"]
        self.__map = Map(game_map, game_state, self.__players_in_game)

        for p in self.__players_in_game.values():
            p.add_map(self.__map)

        self.__update_game(game_state)

    def __end_game(self) -> None:
        if self.__winner:
            winner = self.__players_in_game[self.__winner].name
            print(f"Game winner is {winner}!")
        else:
            print(f"Game is Draw!")

        for client in self.__all_clients.values():
            client.logout()
            client.disconnect()

        pygame.quit()

    def __connect(self, player: Player) -> None:
        self.__all_clients[player] = Client()
        player_info: dict = self.__all_clients[player].login(player.name, player.password, self.__name,
                                                             self.__num_turns, self.__max_players, player.is_observer,
                                                             self.__is_full)
        player.add(player_info, self.__all_clients[player])
        player.start()

        self.__players_in_game[player.id] = player
        self.__current_client = self.__all_clients[player]
