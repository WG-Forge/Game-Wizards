from pygame.time import Clock
from threading import Semaphore
from typing import Optional
from threading import Thread
import random
import time

from src.client.game_client import ServerConnection
from src.map.game_map import Map
from src.players.player_factory import PlayerFactory
from src.players.player import Player
from src.players.remote_player import RemotePlayer


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

        # Observer client used for obtaining information about game
        self.__info_client: ServerConnection = ServerConnection()
        rnd = random.randint(100000, 200000)
        self.__info_client_idx: int = self.__info_client.login(f"Info Client - Game Wizards - {rnd}", game=self.__name,
                                                               num_turns=self.num_turns, num_players=max_players,
                                                               is_observer=True, is_full=self.__is_full)["idx"]

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

    def add_local_player(self, name: str, password: str = None, is_observer: bool = None) -> None:
        if self.__game_players >= self.__max_players:
            is_observer = True

        if not is_observer:
            self.__game_players += 1

        self.__all_players += 1

        if is_observer:
            player_type: str = "observer"
        else:
            player_type: str = "bot_player"

        player: Player = PlayerFactory.create_player(player_type, name, self.__turn_played_sem,
                                                     self.__current_player_idx, self.__game_players - 1, self.running,
                                                     password, is_observer)

        self.__waiting_players.append(player)

    def add_remote_players(self, player_list: list[dict]) -> None:
        for p in player_list:
            if p["idx"] not in self.__players_in_game.keys():
                if not p["is_observer"]:
                    self.__game_players += 1
                    self.__all_players += 1
                player: Player = PlayerFactory.create_player("remote_player", p["name"], self.__turn_played_sem,
                                                             self.__current_player_idx, self.__game_players - 1,
                                                             self.running, is_observer=p["is_observer"])

                player.add(p, self.__info_client)
                self.__players_in_game[p["idx"]] = player

    def run(self) -> None:
        try:
            self.start_game()

            while self.running:

                if not self.__round_started:
                    self.__update_round()

                self.__update_turn()

                self.__release_and_acquire()

        finally:
            self.__end_game()

    def __release_and_acquire(self):
        for player in self.__players_in_game.values():
            player.next_turn_sem.release()

        if not isinstance(self.__current_player, RemotePlayer) and self.running:
            self.__info_client.turn()

        for _ in range(self.__all_players):
            self.__turn_played_sem.acquire()

    def start_game(self) -> None:
        self.running = True
        self.__wait_for_all_players()

        game_state: dict = self.__info_client.game_state()

        self.__max_players = game_state["num_players"]
        self.num_turns = game_state["num_turns"]
        self.num_rounds = game_state["num_rounds"]

        for idx in game_state["player_result_points"].keys():
            self.__player_wins[int(idx)] = 0

        for p in self.__players_in_game.values():
            if not isinstance(p, RemotePlayer) or not p.is_observer:
                p.start()

        self.__update_round()

    def __wait_for_all_players(self) -> None:
        game_state: dict = self.__info_client.game_state()

        # Connect local players
        self.__connect_local_players()

        while len(game_state["players"]) != game_state["num_players"]:
            game_state: dict = self.__info_client.game_state()
            game_map: dict = self.__info_client.map()

            self.add_remote_players(game_state["players"])
            self.add_remote_players(game_state["observers"])
            self.map = Map(game_map, game_state, self.__players_in_game)

            time.sleep(0.1)

    def __update_round(self) -> None:
        self.__round_started = True

        game_map = self.__info_client.map()
        game_state = self.__info_client.game_state()

        self.current_round = game_state["current_round"]
        for player in self.__players_in_game.values():
            player.round_reset()

        self.map = Map(game_map, game_state, self.__players_in_game)

        for player in self.__players_in_game.values():
            player.round_update(self.map)

    def __update_turn(self) -> None:
        game_state = self.__info_client.game_state()

        self.current_turn = game_state["current_turn"]
        self.__current_player_idx = game_state["current_player_idx"]

        print()
        if self.__current_player_idx != 0:
            self.__current_player = self.__players_in_game[self.__current_player_idx]
            self.__current_player.ms_logic.reset_shoot_actions(self.__current_player_idx)
            print(f"Current turn: {self.current_turn}, "
                  f"current player: {self.__current_player.name}")
        else:
            print(f"Current turn: {self.current_turn}")
            self.__current_player = None

        for player in self.__players_in_game.values():
            player.set_curr(self.__current_player_idx)

        # Update map
        self.map.update_map(game_state)

        # Check if round/game is over
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
        self.__info_client.logout()
        self.__info_client.disconnect()

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

    def __connect_local_players(self) -> None:
        for player in self.__waiting_players:
            self.__connect(player)

    def __connect(self, player: Player) -> None:
        game_client = ServerConnection()
        player_info: dict = game_client.login(player.name, player.password, self.__name, self.num_turns,
                                              self.__max_players, player.is_observer, self.__is_full)
        player.add(player_info, game_client)

        self.__players_in_game[player.id] = player
