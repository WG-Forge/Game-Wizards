from threading import Semaphore

from src.players.player import Player
from src.players.bot_player import BotPlayer
from src.players.observer import Observer


class PlayerFactory:
    __PLAYER_TYPES = {
        "bot_player": BotPlayer,
        "observer": Observer
    }

    @staticmethod
    def create_player(player_type: str, name: str, turn_played_sem: Semaphore, current_player_idx: int,
                      player_index: int, running: bool, password: str = None, is_observer: bool = None) -> Player:
        player_class = PlayerFactory.__PLAYER_TYPES[player_type]
        return player_class(name, password, is_observer, turn_played_sem, current_player_idx, player_index, running)
