from threading import Semaphore
from time import sleep

from src.players.player import Player
from src.map.hex import Hex
from src.vehicles.tank import Tank


class BotPlayer(Player):
    def __init__(self, name: str, password: str, is_observer: bool, turn_played_sem: Semaphore,
                 current_player: int, player_index: int) -> None:
        super().__init__(name, password, is_observer, turn_played_sem, current_player, player_index)

    def _play_turn(self) -> None:
        if self._current_player == self.id:
            self._ms_logic.reset_shoot_actions(self.id)
            for tank in self._tanks:
                if not self._shoot(tank):
                    self._move(tank)

        # Uncomment for slower game
        # sleep(1)
        self._client.turn()

    def _shoot(self, tank: Tank) -> bool:
        coord, shoot_list = self._ms_logic.shoot(tank)
        if not coord:
            return False

        self._map.get_painter().draw_shoot_animation(tank, shoot_list)
        self._map.get_painter().draw_attacked_hp(shoot_list, tank.get_damage())

        for t in shoot_list:
            self._map.shoot_update_data(tank, t)

        self._client.shoot({"vehicle_id": tank.get_id(), "target": {"x": coord.q, "y": coord.r, "z": coord.s}})
        tank.set_bonus_range(0)

        return True

    def _move(self, tank: Tank) -> None:
        if self._ms_logic.is_in_base(tank.get_position()):
            return

        move_coord = self._ms_logic.move(tank.get_position(), tank.get_sp())
        if not move_coord:
            return

        self._map.catapult_check(tank, move_coord)
        self._map.heavy_repair_check(tank, move_coord)
        self._map.light_repair_check(tank, move_coord)

        target = {"x": move_coord.q, "y": move_coord.r, "z": move_coord.s}
        move_data = {"vehicle_id": tank.get_id(), "target": target}

        self._map.move_update_data(tank, Hex.dict_to_hex(target))
        self._client.move(move_data)
