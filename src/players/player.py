from abc import abstractmethod
from threading import Thread, Semaphore
from time import sleep

from src.vehicles.tank import Tank
from src.client.game_client import Client
from src.map.game_map import Map


class Player(Thread):
    def __init__(self, name: str, password: str, is_observer: bool, turn_played_sem: Semaphore,
                 current_player: int) -> None:
        super().__init__(daemon=True)
        self.name = name
        self.password = password
        self._tanks: [Tank] = []
        self.__capture_points = 0
        self.__destroyed_points = 0
        self.is_observer = is_observer
        self.id = None
        self._client = None
        self._map = None
        self.__current_player = current_player
        self.__turn_played_sem: Semaphore = turn_played_sem
        self.next_turn_sem: Semaphore = Semaphore(0)

    def __hash__(self):
        return hash(self.name)

    def add(self, player_info: dict, client: Client) -> None:
        self.id: int = player_info["idx"]
        self.is_observer: bool = player_info["is_observer"]
        self.__capture_points = 0
        self.__destroyed_points = 0
        self._client: Client = client

    def add_tank(self, tank: Tank) -> None:
        self._tanks.append(tank)

    def add_map(self, m: Map) -> None:
        self._map = m

    def reorder(self):
        tank_tmp = self._tanks[0]
        self._tanks[0] = self._tanks[4]
        self._tanks[4] = tank_tmp
        tank_tmp = self._tanks[1]
        self._tanks[1] = self._tanks[2]
        self._tanks[2] = tank_tmp

    def set_curr(self, curr: int):
        self.__current_player = curr

    def run(self) -> None:
        while True:
            self.next_turn_sem.acquire()

            if self.__current_player == self.id:
                self._map.reset_shoot_actions(self.id)
                self._play_turn()

            # Uncomment for slower game
            # sleep(1)
            self._client.turn()

            self.__turn_played_sem.release()

    @abstractmethod
    def _play_turn(self):
        pass
