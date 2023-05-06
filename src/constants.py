from enum import IntEnum

# Screen constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
HEX_SIZE = 21


# Client enums
class Action(IntEnum):
    LOGIN = 1
    LOGOUT = 2
    MAP = 3
    GAME_STATE = 4
    GAME_ACTIONS = 5
    TURN = 6
    CHAT = 100
    MOVE = 101
    SHOOT = 102


class Result(IntEnum):
    OKEY = 0
    BAD_COMMAND = 1
    ACCESS_DENIED = 2
    INAPPROPRIATE_GAME_STATE = 3
    TIMEOUT = 4
    INTERNAL_SERVER_ERROR = 500


# Tanks constants
tank_characteristics: dict = {
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
