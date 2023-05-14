from src.map.hex import Hex
from src.constants import tank_characteristics, optimal_hexes


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

        self.tank_color: tuple = tank_color
        self.spawn_color: tuple = spawn_color
        self.path: list = []

    def __str__(self) -> str:
        return f"{self.__tank_id}: {self.__position}"

    def __repr__(self) -> str:
        return f"{self.__tank_id}: {self.__position}"

    def __lt__(self, other) -> bool:
        return self.__hp < other.__hp

    def get_player_id(self) -> int:
        return self.__player_id

    def get_sp(self) -> int:
        return self.__sp

    def get_position(self) -> Hex:
        return self.__position

    def get_spawn_position(self) -> Hex:
        return self.__spawn_position

    def get_hp(self) -> int:
        return self.__hp

    def get_full_hp(self) -> int:
        return self.__full_hp

    def get_cp(self) -> int:
        return self.__capture_points

    def get_id(self) -> int:
        return self.__tank_id

    def get_type(self) -> str:
        return self.__tank_type

    def get_min_range(self) -> int:
        return self.__min_range

    def get_max_range(self) -> int:
        return self.__max_range + self.__bonus_range

    def get_damage(self) -> int:
        return self.__damage

    def get_dp(self) -> int:
        return self.__destruction_points

    def update_position(self, new_position: Hex) -> None:
        self.__position = new_position

    def update_hp(self, new_hp: int) -> None:
        self.__hp = new_hp

    def update_cp(self, new_cp: int) -> None:
        self.__capture_points = new_cp

    def update_dp(self, new_dp: int) -> None:
        self.__destruction_points = new_dp

    def set_bonus_range(self, bonus_range: int) -> None:
        self.__bonus_range = bonus_range

    def get_bonus_range(self) -> int:
        return self.__bonus_range

    def repair(self) -> None:
        self.__hp = self.__full_hp

    def reset(self) -> None:
        self.__hp = self.__full_hp
        self.__position = self.__spawn_position

    # Is this tank at his optimal hex?
    def optimal_hex(self) -> bool:
        if self.get_position().hex_abs() == optimal_hexes[self.get_type()]:
            return True
        return False

    def repair_needed(self) -> bool:
        if self.get_hp() != self.get_full_hp():
            return True
        return False
