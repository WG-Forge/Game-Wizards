from threading import Semaphore

from src.players.player import Player
from src.map.hex import Hex


class RemotePlayer(Player):
    def __init__(self, name: str, password: str, is_observer: bool, turn_played_sem: Semaphore,
                 current_player: int, player_index: int, running: bool):
        super().__init__(name, password, is_observer, turn_played_sem, current_player, player_index, running)

    def _play_turn(self) -> None:
        if self._current_player == self.id:
            # Force the turn
            self._client.turn()
            # Last turn actions
            remote_actions: list[dict] = self._client.game_actions()["actions"]
            print(remote_actions)

            for action in remote_actions:
                action_type: int = action["action_type"]
                tank_id: int = action["data"]["vehicle_id"]
                target_hex: Hex = Hex.dict_to_hex(action["data"]["target"])

                for t in self._tanks:
                    if t.id == tank_id:
                        if action_type == 101:
                            self._map.move_update_data(t, target_hex)
                        else:
                            if t.type != "at_spg":
                                self._map.shoot_update_data(t, self._ms_logic.tank_from_hex(target_hex))
                            else:
                                self._ms_logic.at_spg_shoot_update(t, target_hex)

    # No need to disconnect remote player
    def _disconnect(self) -> None:
        pass
