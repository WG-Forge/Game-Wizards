from abc import abstractmethod, ABC
from threading import Thread, Semaphore
from typing import Optional

from src.logic import MSLogic
from src.vehicles.tank import Tank
from src.client.game_client import ServerConnection
from src.map.game_map import Map
from src.constants import TANK_COLORS, SPAWN_COLORS


class Player(Thread, ABC):
    def __init__(self, name: str, password: str, is_observer: bool, turn_played_sem: Semaphore,
                 current_player: int, player_index: int, running: bool) -> None:
        super().__init__()

        self.name: str = name
        self.password: str = password
        self.is_observer: bool = is_observer
        self.id: Optional[int] = None

        self._tanks: list[Tank] = []
        self.__capture_points: int = 0
        self.__destroyed_points: int = 0

        self._client: Optional[ServerConnection] = None
        self._map: Optional[Map] = None
        self._ms_logic: Optional[MSLogic] = None
        self._current_player: int = current_player
        self.__running = running

        self.__turn_played_sem: Semaphore = turn_played_sem
        self.next_turn_sem: Semaphore = Semaphore(0)

        self.tank_color: tuple = TANK_COLORS[player_index]
        self.spawn_color: tuple = SPAWN_COLORS[player_index]

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Player {self.id}: {self.name}, obs: {self.is_observer}"

    @property
    def capture_points(self) -> int:
        self.__capture_points = sum(tank.cp for tank in self._tanks)
        return self.__capture_points

    @property
    def destruction_points(self) -> int:
        self.__destroyed_points = sum(tank.dp for tank in self._tanks)
        return self.__destroyed_points

    @property
    def ms_logic(self) -> MSLogic:
        return self._ms_logic

    def add(self, player_info: dict, client: ServerConnection) -> None:
        self.id = player_info["idx"]
        self.is_observer = player_info["is_observer"]
        self.__capture_points = 0
        self.__destroyed_points = 0
        self._client = client

    def add_tank(self, tank: Tank) -> None:
        self._tanks.append(tank)

    def round_update(self, m: Map) -> None:
        self._map = m
        self._ms_logic = MSLogic(self._map)

    def reorder(self) -> None:
        tank_tmp = self._tanks[0]
        self._tanks[0] = self._tanks[4]
        self._tanks[4] = tank_tmp
        tank_tmp = self._tanks[1]
        self._tanks[1] = self._tanks[2]
        self._tanks[2] = tank_tmp

    def set_curr(self, curr: int) -> None:
        self._current_player = curr

    def stop_player(self) -> None:
        self.__running = False

    def round_reset(self) -> None:
        self._tanks = []

    def run(self) -> None:
        while self.__running:
            self.next_turn_sem.acquire()

            try:
                if not self.__running:
                    break

                self._play_turn()
            finally:
                self.__turn_played_sem.release()

        self._disconnect()

    @abstractmethod
    def _play_turn(self) -> None:
        pass

    @abstractmethod
    def _disconnect(self) -> None:
        pass
