from threading import Semaphore
from typing import Optional

from src.players.player import Player
from src.map.hex import Hex
from src.vehicles.tank import Tank


class BotPlayer(Player):
    def __init__(self, name: str, password: str, is_observer: bool, turn_played_sem: Semaphore,
                 current_player: int, player_index: int, running: bool) -> None:
        super().__init__(name, password, is_observer, turn_played_sem, current_player, player_index, running)

    def _play_turn(self) -> None:
        if self._current_player == self.id:
            self._ms_logic.reset_shoot_actions(self.id)
            for tank in self._tanks:
                self._map.catapult_check(tank, tank.position)
                self._tactic(tank)

        self._client.turn()

    def _shoot(self, tank: Tank) -> bool:
        coord, shoot_list = self._ms_logic.shoot(tank)
        if not coord:
            return False

        self._map.painter.draw_shoot_animation(tank, shoot_list)
        self._map.painter.draw_attacked_hp(shoot_list, tank.damage)

        for t in shoot_list:
            self._map.shoot_update_data(tank, t)

        self._client.shoot({"vehicle_id": tank.id, "target": {"x": coord.q, "y": coord.r, "z": coord.s}})
        tank.set_bonus_range(0)

        return True

    def _tactic(self, tank: Tank) -> None:

        move_coord = self._ms_logic.move(tank.position, tank)

        if tank.type == "light_tank":
            move_coord = self.light_tank_tactic(tank)
        elif tank.type == "medium_tank":
            move_coord = self.medium_tank_tactic(tank)
        elif tank.type == "heavy_tank":
            move_coord = self.heavy_tank_tactic(tank)
        elif tank.type == "spg":
            move_coord = self.spg_tactic(tank)
        elif tank.type == "at_spg":
            move_coord = self.tank_destroyer_tactic(tank)

        if not move_coord:
            return

        self._map.catapult_check(tank, tank.position)
        self._map.heavy_repair_check(tank, move_coord)
        self._map.light_repair_check(tank, move_coord)

        target = {"x": move_coord.q, "y": move_coord.r, "z": move_coord.s}
        move_data = {"vehicle_id": tank.id, "target": target}

        self._map.move_update_data(tank, Hex.dict_to_hex(target))
        self._client.move(move_data)

    def has_clear_path(self, tank: Tank, hex: Hex) -> bool:
        for t in self._map.tanks.values():
            if t.id == tank.id:
                continue
            if t.position == hex:
                return False
        return True

    def light_tank_tactic(self, tank: Tank) -> Optional[Hex]:
        """
        if you can shoot someone - do it
        if you can't, and you are already in your optimal hex, and you have bonus range, camp there
        if you aren't in your optimal hex, and you have bonus, move
        if you don't have bonus, go get it
        :param tank:
        :return:
        """
        if self._shoot(tank):
            return None
        elif tank.optimal_hex() and tank.bonus_range != 0:
            return
        elif not tank.optimal_hex() and tank.bonus_range != 0:
            return self._ms_logic.move(tank.position, tank)

        elif (len(tank.path) == 0 and tank.bonus_range == 0) \
                or (len(tank.path) != 0 and tank.position == tank.spawn_position):
            catapult_list = sorted(self._map.catapult.keys(),
                                   key=lambda hexagon: Hex.distance(tank.position, hexagon))
            tank.path = self._ms_logic.a_star(tank.position, catapult_list[0])
            if len(tank.path) >= tank.sp and self.has_clear_path(tank, tank.path[2]):
                tank.path.pop(0)
                tank.path.pop(0)
                return tank.path.pop(0)
        elif len(tank.path) != 0 and tank.bonus_range == 0:
            if len(tank.path) >= tank.sp and self.has_clear_path(tank, tank.path[2]):
                tank.path.pop(0)
                tank.path.pop(0)
                return tank.path.pop(0)
            elif len(tank.path) >= tank.sp - 1 and self.has_clear_path(tank, tank.path[1]):
                tank.path.pop(0)
                return tank.path.pop(0)
            elif len(tank.path) >= tank.sp - 2 and self.has_clear_path(tank, tank.path[0]):
                return tank.path.pop(0)

        return None

    def medium_tank_tactic(self, tank: Tank) -> Optional[Hex]:
        """
        If you get killed - reset the path
        Assuming that you will kill the target with your shot:
        if you will not be killed - shoot it
        if you can get killed and you are not in the base - run for the repair
        if you are not in your optimal hex, and you can't shoot, move
        :param tank:
        :return:
        """
        if tank.position == tank.spawn_position:
            tank.path = []
        if (list(self._ms_logic.can_be_shot(tank.player_id, tank.position).values())[0] - 1 < tank.hp
                    or self._ms_logic.is_in_base(tank.position)) and self._shoot(tank):
            return None
        elif list(self._ms_logic.can_be_shot(tank.player_id, tank.position).values())[0] >= tank.hp \
                and not self._ms_logic.is_in_base(tank.position) and len(tank.path) == 0 and tank.repair_needed():
            light_list = sorted(self._map.light_repair,
                                key=lambda hexagon: Hex.distance(tank.position, hexagon))
            tank.path = self._ms_logic.a_star(tank.position, light_list[0])
            if len(tank.path) >= tank.sp and self.has_clear_path(tank, tank.path[1]):
                tank.path.pop(0)
                return tank.path.pop(0)
        elif len(tank.path) != 0 and tank.repair_needed():
            if len(tank.path) >= tank.sp and self.has_clear_path(tank, tank.path[1]):
                tank.path.pop(0)
                return tank.path.pop(0)
            elif len(tank.path) == tank.sp - 1 and self.has_clear_path(tank, tank.path[0]):
                return tank.path.pop(0)
        elif not tank.optimal_hex() and not self._shoot(tank):
            return self._ms_logic.move(tank.position, tank)

    def heavy_tank_tactic(self, tank: Tank) -> Optional[Hex]:
        """
        If you get killed - reset the path
        Assuming that you will kill the target with your shot:
        if you will not be killed - shoot it
        if you can get killed and you are not in the base - run for the repair
        if you are not in your optimal hex, and you can't shoot, move
        :param tank:
        :return:
        """
        if tank.position == tank.spawn_position:
            tank.path = []
        if (list(self._ms_logic.can_be_shot(tank.player_id, tank.position).values())[0] - 1 < tank.hp
                    or self._ms_logic.is_in_base(tank.position)) and self._shoot(tank):
            return None
        elif list(self._ms_logic.can_be_shot(tank.player_id, tank.position).values())[0] >= tank.hp \
                and not self._ms_logic.is_in_base(tank.position) and len(tank.path) == 0 and tank.repair_needed():
            heavy_list = sorted(self._map.heavy_repair,
                                key=lambda hexagon: Hex.distance(tank.position, hexagon))
            tank.path = self._ms_logic.a_star(tank.position, heavy_list[0])
            if len(tank.path) >= tank.sp and self.has_clear_path(tank, tank.path[0]):
                return tank.path.pop(0)
        elif len(tank.path) != 0 and tank.repair_needed():
            if len(tank.path) >= tank.sp and self.has_clear_path(tank, tank.path[0]):
                return tank.path.pop(0)
        elif not tank.optimal_hex() and not self._shoot(tank):
            return self._ms_logic.move(tank.position, tank)

    def spg_tactic(self, tank: Tank) -> Optional[Hex]:
        """
        Your job is to cover catapult hex that light tank is capturing
        Shoot if you can
        Go into the closest hex to the center from the 3rd ring of the catapult, that your light tank is fighting for
        :param tank:
        :return:
        """
        if tank.position == tank.spawn_position:
            tank.path = []
        if self._shoot(tank):
            return
        elif len(tank.path) == 0:
            catapult_list = sorted(self._map.catapult.keys(),
                                   key=lambda hexagon: Hex.distance(tank.position, hexagon))
            closest_to_center = sorted(Hex.hex_ring(catapult_list[0], 3),
                                       key=lambda hexagon: Hex.distance(Hex(0, 0, 0), hexagon))
            for h in self._map.obstacles:
                if h in closest_to_center:
                    closest_to_center.remove(h)
            tank.path = self._ms_logic.a_star(tank.position, closest_to_center[1])
            if len(tank.path) >= tank.sp and self.has_clear_path(tank, tank.path[0]):
                return tank.path.pop(0)
        elif len(tank.path) != 0:
            if len(tank.path) >= tank.sp and self.has_clear_path(tank, tank.path[0]):
                return tank.path.pop(0)

        return

    def tank_destroyer_tactic(self, tank: Tank) -> Optional[Hex]:
        """
        Assume that you are blocking your own tank if there are more than 2 obstacles and heavy tank in your 1st ring,
        so move forward
        Shoot if you can
        Move forward if you aren't at your optimal hex
        :param tank:
        :return:
        """
        if self._shoot(tank):
            return
        td_radius = Hex.hex_ring(tank.position, 1)
        num_of_obstacles = 0
        for h in self._map.obstacles:
            if h in td_radius:
                num_of_obstacles += 1
        for t in self._map.tanks.values():
            if t.type == "heavy_tank" and t.player_id == tank.player_id and num_of_obstacles >= 2:
                return self._ms_logic.move(tank.position, tank)
        if not tank.optimal_hex():
            return self._ms_logic.move(tank.position, tank)

        return
