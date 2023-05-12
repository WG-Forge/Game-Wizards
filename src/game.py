import pygame
from pygame.time import Clock
from threading import Semaphore
from typing import Optional
from threading import Thread

from src.client.game_client import Client
from src.map.game_map import Map
from src.players.player_factory import PlayerFactory
from src.players.player import Player


class Game(Thread):
    def __init__(self, name: str = None, max_players: int = 1, num_turns: int = None, is_full: bool = False) -> None:
        super().__init__()

        self.__name: str = name
        self.map: Optional[Map] = None
        self.running: bool = True
        self.__winner: Optional[int] = None
        self.__is_full: bool = is_full

        self.num_turns: int = num_turns
        self.current_turn: Optional[int] = None
        self.num_rounds: Optional[int] = None
        self.current_round: Optional[int] = None
        self.__round_started: bool = False

        self.__current_client: Client = Client()
        self.__all_clients: dict[Player, Client] = {}

        self.__current_player: Optional[Player] = None
        self.__waiting_players: list[Player] = []
        self.__players_in_game: dict[int, Player] = {}
        self.__player_wins: dict[int, int] = {}

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
                                             self.__game_players - 1, self.running, password, is_observer)

        self.__waiting_players.append(player)

    def run(self) -> None:
        self.__start_game()

        while self.running:

            if not self.__round_started:
                self.__update_round()

            self.__update_turn()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.map.draw_map(self.current_turn, self.num_turns, self.current_round, self.num_rounds)

            self.__clock.tick(60)

            for player in self.__players_in_game.values():
                player.next_turn_sem.release()

            for _ in range(self.__all_players):
                self.__turn_played_sem.acquire()

        self.__end_game()

    def __start_game(self) -> None:
        self.running = True
        self.__connect_players()

        game_state: dict = self.__current_client.game_state()

        self.__max_players = game_state["num_players"]
        self.num_turns = game_state["num_turns"]
        self.num_rounds = game_state["num_rounds"]

        for idx in game_state["player_result_points"].keys():
            self.__player_wins[int(idx)] = 0

    def __update_round(self) -> None:
        self.__round_started = True

        game_map = self.__current_client.map()
        game_state = self.__current_client.game_state()

        self.current_round = game_state["current_round"]
        for player in self.__players_in_game.values():
            player.round_reset()

        self.map = Map(game_map, game_state, self.__players_in_game)

        for player in self.__players_in_game.values():
            player.round_update(self.map)

    def __update_turn(self) -> None:
        game_state = self.__current_client.game_state()

        self.current_turn = game_state["current_turn"]
        self.__current_player_idx = game_state["current_player_idx"]

        print()
        if self.__current_player_idx != 0:
            self.__current_player = self.__players_in_game[self.__current_player_idx]
            self.__current_client = self.__all_clients[self.__current_player]
            print(f"Current turn: {self.current_turn}, "
                  f"current player: {self.__current_player.name}")
        else:
            print(f"Current turn: {self.current_turn}")
            self.__current_player = None

        for player in self.__players_in_game.values():
            player.set_curr(self.__current_player_idx)

        self.map.update_map(game_state)

        if game_state["finished"]:
            self.__winner = game_state["winner"]
            if self.__winner:
                self.__player_wins[self.__winner] += 1
            self.__round_result()

            if game_state["current_round"] == self.num_rounds:
                self.running = False
                for player in self.__players_in_game.values():
                    player.stop_player()
            else:
                self.__round_started = False

    def __end_game(self) -> None:
        self.__game_result()
        self.__disconnect_players()

        pygame.quit()

    def __round_result(self) -> None:
        print()
        if self.__winner:
            winner = self.__players_in_game[self.__winner].name
            print(f"Round winner is {winner}!")
        else:
            print("Round is Draw!")

    def __game_result(self) -> None:
        winner = None
        max_points: int = -1
        min_points: int = 100

        print()
        for idx, win_points in self.__player_wins.items():
            print(f"{self.__players_in_game[idx]} win points: {win_points}")

            if win_points > max_points:
                winner = self.__players_in_game[idx]
                max_points = win_points

            min_points = min(min_points, win_points)

        if max_points != min_points or len(self.__player_wins) == 1:
            print(f"Game winner is {winner}!")
        else:
            print("Game is Draw!")

    def __connect_players(self) -> None:
        for player in self.__waiting_players:
            self.__connect(player)

    def __disconnect_players(self) -> None:
        for client in self.__all_clients.values():
            client.logout()
            client.disconnect()

    def __connect(self, player: Player) -> None:
        self.__all_clients[player] = Client()
        player_info: dict = self.__all_clients[player].login(player.name, player.password, self.__name,
                                                             self.num_turns, self.__max_players, player.is_observer,
                                                             self.__is_full)
        player.add(player_info, self.__all_clients[player])
        player.start()

        self.__players_in_game[player.id] = player
        self.__current_client = self.__all_clients[player]
