from typing import Any, Optional
from pygame import Surface

from src.map.hex import Hex
from src.gui.painter import Painter
from src.vehicles.tank import Tank
from src.gui.explosion import Explosion


class Map:
    def __init__(self, game_map: dict, game_state: dict, players_in_game: dict) -> None:
        self.__map: dict[Hex, dict] = {}
        self.__painter: Optional[Painter] = None
        self.__tanks: dict[int, Tank] = {}
        self.__tank_positions: dict[int, Hex] = {}

        self.__base: list[Hex] = []
        self.__obstacles: list[Hex] = []
        self.__spawn: list[Hex] = []
        self.__light_repair: list[Hex] = []
        self.__heavy_repair: list[Hex] = []
        self.__catapult: dict[Hex, int] = {}

        self.__shoot_actions: dict[int, []] = {}
        self.__players: list = []
        self.__initialize_map(game_map, game_state, players_in_game)

    def __initialize_map(self, game_map: dict, game_state: dict, players_in_game: dict) -> None:
        self.__map = {h: {"type": "empty", "tank": None} for h in Hex.hex_spiral(Hex(0, 0, 0), game_map["size"])}

        for idx, player in players_in_game.items():
            if not player.is_observer:
                self.__players.append(player)

        for p in self.__players:
            self.__shoot_actions[p.id] = []

        for tank_id, tank_info in game_state["vehicles"].items():
            player = players_in_game[tank_info["player_id"]]
            tank = Tank(int(tank_id), tank_info, player.tank_color, player.spawn_color)
            self.__tanks[int(tank_id)] = tank
            player.add_tank(tank)
            self.__map[Hex.dict_to_hex(tank_info["spawn_position"])]["tank"] = tank
            self.__spawn.append(Hex.dict_to_hex(tank_info["spawn_position"]))

        for player in players_in_game.values():
            if not player.is_observer:
                player.reorder()

        for h, positions in game_map["content"].items():
            for position in positions:
                new_hex = Hex.dict_to_hex(position)
                if h == "base":
                    self.__map[new_hex]["type"] = "base"
                    self.__base.append(new_hex)
                elif h == "obstacle":
                    self.__map[new_hex]["type"] = "obstacle"
                    self.__obstacles.append(new_hex)
                elif h == "light_repair":
                    self.__map[new_hex]["type"] = "light_repair"
                    self.__light_repair.append(new_hex)
                elif h == "hard_repair":
                    self.__map[new_hex]["type"] = "heavy_repair"
                    self.__heavy_repair.append(new_hex)
                elif h == "catapult":
                    self.__map[new_hex]["type"] = "catapult"
                    self.__catapult[new_hex] = 3
        self.__painter = Painter(self.__map, self.__players)

    def update_map(self, game_state: dict) -> None:
        for tank_id, tank_info in game_state["vehicles"].items():
            tank_id = int(tank_id)
            self.__tank_positions[tank_id] = Hex.dict_to_hex(tank_info["position"])
            server_position = Hex.dict_to_hex(tank_info["position"])
            server_hp = tank_info["health"]
            server_cp = tank_info["capture_points"]

            tank = self.__tanks[tank_id]
            tank_position = tank.position
            tank_hp = tank.hp
            tank_cp = tank.cp

            if server_position != tank_position:
                self.move_update_data(tank, server_position)
            if server_hp != tank_hp:
                tank.update_hp(server_hp)
            if server_cp != tank_cp:
                tank.update_cp(server_cp)

    def draw_map(self, screen: Surface, current_turn: int, num_turns: int, current_round: int, num_rounds: int) -> None:
        self.__painter.draw(screen, current_turn, num_turns, current_round, num_rounds)

    @property
    def painter(self) -> Painter:
        return self.__painter

    @property
    def map(self) -> dict[Hex, dict]:
        return self.__map

    @property
    def tank_positions(self) -> dict[int, Hex]:
        return self.__tank_positions

    @property
    def tanks(self) -> dict[int, Tank]:
        return self.__tanks

    @property
    def base(self) -> list[Hex]:
        return self.__base

    @property
    def obstacles(self) -> list[Hex]:
        return self.__obstacles

    @property
    def spawn(self) -> list[Hex]:
        return self.__spawn

    @property
    def players(self) -> list:
        return self.__players

    @property
    def shoot_actions(self) -> dict[int, Any]:
        return self.__shoot_actions

    @property
    def heavy_repair(self) -> list[Hex]:
        return self.__heavy_repair

    @property
    def light_repair(self) -> list[Hex]:
        return self.__light_repair

    @property
    def catapult(self) -> dict[Hex, int]:
        return self.__catapult

    def move_update_data(self, tank: Tank, coord: Hex) -> None:
        self.__tank_positions[tank.id] = coord
        tank.update_position(coord)

    def shoot_update_data(self, tank: Tank, tank2: Tank) -> None:
        self.painter.add_shoot_animation(tank.position, tank2.position)
        if tank2.hp - tank.damage <= 0:
            self.painter.explosion_group.add(Explosion(Hex.hex_to_pixel(tank2.position.q, tank2.position.r)))
            tank.update_dp(tank.dp + tank2.full_hp)
            tank2.reset()
        else:
            tank2.update_hp(tank2.hp - tank.damage)

        self.__shoot_actions[tank.player_id].append(tank2.player_id)

    def catapult_check(self, tank: Tank, move_coord: Hex) -> None:
        if move_coord in self.__catapult.keys() and self.__catapult[move_coord] > 0:
            tank.update_bonus_range()
            self.__catapult[move_coord] -= 1

    def heavy_repair_check(self, tank: Tank, move_coord: Hex) -> None:
        tank_type = tank.type
        if (tank_type == "heavy_tank" or tank_type == "at_spg") and move_coord in self.__heavy_repair:
            tank.repair()

    def light_repair_check(self, tank: Tank, move_coord: Hex) -> None:
        tank_type = tank.type
        if tank_type == "medium_tank" and move_coord in self.__light_repair:
            tank.repair()
