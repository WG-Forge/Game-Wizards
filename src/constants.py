from enum import IntEnum

# Server info
SERVER_HOST = "wgforge-srv.wargaming.net"
SERVER_PORT = 443
MAX_MESSAGE_SIZE = 8192

HOST_PORT = 443
HOST_NAME = "wgforge-srv.wargaming.net"
BYTES_IN_INT = 4

# Screen info
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
HEX_SIZE = 21

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BASE_COLOR = (144, 238, 144)
OBSTACLE_COLOR = (127, 127, 127)
HP_COLOR = (2, 113, 72)
RED = (255, 0, 0)
TANK_COLORS = ((237, 41, 57), (70, 191, 224), (224, 206, 70))
SPAWN_COLORS = ((255, 198, 196), (173, 216, 230), (255, 250, 205))


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


# Tank info
tank_characteristics: dict = {
    "spg": {
        "sp": 1,
        "min_range": 3,
        "max_range": 3
    },
    "light_tank": {
        "sp": 3,
        "min_range": 2,
        "max_range": 2
    },
    "heavy_tank": {
        "sp": 1,
        "min_range": 1,
        "max_range": 2
    },
    "medium_tank": {
        "sp": 2,
        "min_range": 2,
        "max_range": 2
    },
    "at_spg": {
        "sp": 1,
        "min_range": 1,
        "max_range": 3
    }
}

# Image paths
SPG_PATH = "src/assets/vehicle_types/spg.png"
LT_PATH = "src/assets/vehicle_types/light_tank.png"
HT_PATH = "src/assets/vehicle_types/heavy_tank.png"
MT_PATH = "src/assets/vehicle_types/medium_tank.png"
TD_PATH = "src/assets/vehicle_types/at_spg.png"

CATA_PATH = "src/assets/special_hexes/catapult.png"
HR_PATH = "src/assets/special_hexes/heavy_repair.png"
LR_PATH = "src/assets/special_hexes/light_repair.png"

BACKGROUND_PATH = "src/assets/screen/background.jpg"
ICON_PATH = "src/assets/screen/icon.png"

# Legend
LEGEND_ORDER = [SPG_PATH, LT_PATH, HT_PATH, MT_PATH, TD_PATH, CATA_PATH, HR_PATH, LR_PATH]
LEGEND_POSITIONS = [(-15, 12, 3), (-14, 12, 2), (-13, 12, 1), (-12, 12, 0),
                    (-11, 12, -1), (0, 12, -12), (1, 12, -13), (2, 12, -14)]
LEGEND_TEXT = ["SPG", "LIGHT TANK", "HEAVY TANK", "MEDIUM TANK", "TANK DESTROYER",
               "CATAPULT", "HEAVY REPAIR", "LIGHT REPAIR"]
LEGEND_TEXT_POSITION = [(1005, 56), (1005, 93), (1005, 130), (1005, 167),
                        (1005, 204), (1005, 601), (1005, 638), (1005, 675)]
LEGEND_NAME = ["spg", "light_tank", "heavy_tank", "medium_tank", "at_spg", "catapult", "heavy_repair", "light_repair"]

# abs values of optimal hex coordinates for each tank
OPTIMAL_HEXES = {
    "spg": 6,
    "light_tank": 6,
    "heavy_tank": 2,
    "medium_tank": 2,
    "at_spg": 4
}
