from src.map.hex import Hex
from src.map.hex_utils import HexUtils


class Tank:
    __characteristics: dict = {
        "light_tank": {
            "sp": 3,
            "min_range": 2,
            "max_range": 2
        },
        "medium_tank": {
            "sp": 2,
            "min_range": 2,
            "max_range": 2
        },
        "heavy_tank": {
            "sp": 1,
            "min_range": 1,
            "max_range": 2
        },
        "spg": {
            "sp": 1,
            "min_range": 3,
            "max_range": 3
        },
        "at_spg": {
            "sp": 1,
            "min_range": 1,
            "max_range": 3
        }
    }

    def __init__(self, tank_id: int, tank_data: dict) -> None:
        self.__tank_id: int = tank_id
        self.__player_id: int = tank_data["player_id"]
        self.__tank_type: str = tank_data["vehicle_type"]
        self.__hp: int = tank_data["health"]
        self.__full_hp: int = self.__hp
        self.__sp: int = Tank.__characteristics[self.__tank_type]["sp"]
        self.__min_range: int = Tank.__characteristics[self.__tank_type]["min_range"]
        self.__max_range: int = Tank.__characteristics[self.__tank_type]["max_range"]
        self.__bonus_range: int = 0
        self.__damage: int = 1
        self.__capture_points: int = tank_data["capture_points"]
        self.__spawn_position: Hex = HexUtils.dict_to_hex(tank_data["spawn_position"])
        self.__position: Hex = self.__spawn_position

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

    def update_position(self, new_position: Hex) -> None:
        self.__position = new_position

    def update_hp(self, new_hp: int) -> None:
        self.__hp = new_hp

    def update_cp(self, new_cp: int) -> None:
        self.__capture_points = new_cp

    def set_bonus_range(self, bonus_range: int) -> None:
        self.__bonus_range = bonus_range

    def repair(self) -> None:
        self.__hp = self.__full_hp

    def reset(self) -> None:
        self.__hp = self.__full_hp
        self.__position = self.__spawn_position
