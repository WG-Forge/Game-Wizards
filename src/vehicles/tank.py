from src.map.hex import Hex
from src.constants import tank_characteristics, OPTIMAL_HEXES


class Tank:
    def __init__(self, tank_id: int, tank_data: dict, tank_color: tuple, spawn_color: tuple) -> None:
        self.__tank_id: int = tank_id
        self.__player_id: int = tank_data["player_id"]
        self.__tank_type: str = tank_data["vehicle_type"]

        self.__hp: int = tank_data["health"]
        self.__full_hp: int = self.__hp
        self.__sp: int = tank_characteristics[self.__tank_type]["sp"]

        self.__min_range: int = tank_characteristics[self.__tank_type]["min_range"]
        self.__max_range: int = tank_characteristics[self.__tank_type]["max_range"]
        self.__bonus_range: int = 0
        self.__damage: int = 1

        self.__capture_points: int = tank_data["capture_points"]
        self.__destruction_points: int = 0

        self.__spawn_position: Hex = Hex.dict_to_hex(tank_data["spawn_position"])
        self.__position: Hex = self.__spawn_position
        self.path: list = []

        self.tank_color: tuple = tank_color
        self.spawn_color: tuple = spawn_color

    def __str__(self) -> str:
        return f"{self.__tank_id}: {self.__position}"

    def __repr__(self) -> str:
        return f"{self.__tank_id}: {self.__position}"

    def __lt__(self, other) -> bool:
        return self.__hp < other.__hp

    @property
    def player_id(self) -> int:
        return self.__player_id

    @property
    def sp(self) -> int:
        return self.__sp

    @property
    def position(self) -> Hex:
        return self.__position

    @property
    def spawn_position(self) -> Hex:
        return self.__spawn_position

    @property
    def hp(self) -> int:
        return self.__hp

    @property
    def full_hp(self) -> int:
        return self.__full_hp

    @property
    def cp(self) -> int:
        return self.__capture_points

    @property
    def id(self) -> int:
        return self.__tank_id

    @property
    def type(self) -> str:
        return self.__tank_type

    @property
    def min_range(self) -> int:
        return self.__min_range

    @property
    def max_range(self) -> int:
        return self.__max_range + self.__bonus_range

    @property
    def damage(self) -> int:
        return self.__damage

    @property
    def dp(self) -> int:
        return self.__destruction_points

    @property
    def bonus_range(self) -> int:
        return self.__bonus_range

    def update_position(self, new_position: Hex) -> None:
        self.__position = new_position

    def update_hp(self, new_hp: int) -> None:
        self.__hp = new_hp

    def update_cp(self, new_cp: int) -> None:
        self.__capture_points = new_cp

    def update_dp(self, new_dp: int) -> None:
        self.__destruction_points = new_dp

    def update_bonus_range(self) -> None:
        self.__bonus_range = 1

    def reset_bonus_range(self) -> None:
        self.__bonus_range = 0

    def repair(self) -> None:
        self.__hp = self.__full_hp

    def reset(self) -> None:
        self.__hp = self.__full_hp
        self.__position = self.__spawn_position

    # Is this tank at his optimal hex?
    def optimal_hex(self) -> bool:
        if abs(self.position) == OPTIMAL_HEXES[self.type]:
            return True
        return False

    def repair_needed(self) -> bool:
        if self.hp != self.full_hp:
            return True
        return False
