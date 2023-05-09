from abc import abstractmethod, ABC
from threading import Thread, Semaphore
from typing import Optional

from src.vehicles.tank import Tank
from src.client.game_client import Client
from src.map.game_map import Map
from src.constants import TANK_COLORS, SPAWN_COLORS


class Player(Thread, ABC):
    def __init__(self, name: str, password: str, is_observer: bool, turn_played_sem: Semaphore,
                 current_player: int, player_index: int) -> None:
        super().__init__(daemon=True)
        self.name: str = name
        self.password: str = password
        self._tanks: list[Tank] = []
        self.__capture_points: int = 0
        self.__destroyed_points: int = 0
        self.is_observer: bool = is_observer
        self.id: Optional[int] = None
        self._client: Optional[Client] = None
        self._map: Optional[Map] = None
        self._current_player: int = current_player

        self.__turn_played_sem: Semaphore = turn_played_sem
        self.next_turn_sem: Semaphore = Semaphore(0)

        self.tank_color: tuple = TANK_COLORS[player_index]
        self.spawn_color: tuple = SPAWN_COLORS[player_index]

    def __hash__(self) -> int:
        return hash(self.name)

    def add(self, player_info: dict, client: Client) -> None:
        self.id = player_info["idx"]
        self.is_observer = player_info["is_observer"]
        self.__capture_points = 0
        self.__destroyed_points = 0
        self._client = client

    def add_tank(self, tank: Tank) -> None:
        self._tanks.append(tank)

    def add_map(self, m: Map) -> None:
        self._map = m

    def reorder(self) -> None:
        tank_tmp = self._tanks[0]
        self._tanks[0] = self._tanks[4]
        self._tanks[4] = tank_tmp
        tank_tmp = self._tanks[1]
        self._tanks[1] = self._tanks[2]
        self._tanks[2] = tank_tmp

    def set_curr(self, curr: int) -> None:
        self._current_player = curr

    def run(self) -> None:
        while True:
            self.next_turn_sem.acquire()

            self._play_turn()

            self.__turn_played_sem.release()

    @abstractmethod
    def _play_turn(self) -> None:
        pass
