import random
from typing import Optional, Any

from src.map.game_map import Map
from src.map.hex import Hex
from src.vehicles.tank import Tank


# move-shoot logic
class MSLogic:

    def __init__(self, game_map: Map):
        self.__map = game_map

    def move(self, start: Hex, movement: int) -> Hex:
        visited = []
        rings = [[start]]
        for k in range(1, movement + 1):
            rings.append([])
            for h in rings[k - 1]:
                for direction in range(6):
                    neighbor = Hex.hex_neighbor(h, direction)
                    if neighbor not in visited and neighbor not in self.__map.get_obstacles() \
                            and not self.__offTheGridDetection(neighbor):
                        visited.append(neighbor)
                        rings[k].append(neighbor)

        visited = [h for h in visited if h not in self.__map.get_spawn()
                   and h not in self.__map.get_tank_positions().values()]
        visited.sort(key=lambda x: x)

        move_to = []
        if visited:
            d = Hex.distance(Hex(0, 0, 0), visited[0])
            move_to = [h for h in visited if Hex.distance(Hex(0, 0, 0), h) == d]

        return random.choice(move_to) if visited else None

    def shoot(self, tank: Tank) -> tuple[Optional[Hex], Optional[list[Tank]]]:
        if tank.get_type() != "at_spg":
            return self.__curved_trajectory(tank)
        else:
            return self.__straight_trajectory(tank)

    def __curved_trajectory(self, tank: Tank) -> tuple[Optional[Hex], Optional[list[Tank]]]:
        # Shoot coords based on tank position
        shoot_coords = self.__shoot_coords(tank)

        # Blocked hexes
        blocked = []

        # Add obstacles to blocked
        for coord in shoot_coords:
            if coord in self.__map.get_obstacles():
                blocked.append(coord)

        # Add to blocked my and neutral tanks
        for t in self.__map.get_tanks().values():
            if t.get_player_id() == tank.get_player_id() or self.__neutrality_check(tank, t):
                blocked.append(t.get_position())

        # Enemy tanks
        enemy_tanks = []

        # Add enemy tanks to list
        for t in self.__map.get_tanks().values():
            if t.get_position() not in blocked:
                enemy_tanks.append(t.get_position())

        # Keep only coords that are not blocked and in enemy_tanks
        shoot_coords = [coord for coord in shoot_coords if coord not in blocked and coord in enemy_tanks]

        # From hex list make tank list
        tank_shoot_coords = [self.__tank_from_hex(h) for h in shoot_coords]

        # Keep tanks whose hp is > 0 and sort them based on hp
        tank_shoot_coords = [t for t in tank_shoot_coords if t.get_hp() > 0]
        tank_shoot_coords.sort(key=lambda tt: tt)

        # Shoot at tank with the lowest hp
        if tank_shoot_coords:
            return tank_shoot_coords[0].get_position(), [tank_shoot_coords[0]]
        else:
            return None, None

    def __straight_trajectory(self, tank: Tank) -> tuple[Optional[Hex], Optional[list[Tank]]]:
        # Shoot coords based on tank position
        shoot_coords = self.__shoot_coords(tank)
        x, y, z = tank.get_position()

        # Blocked hexes
        blocked = []

        # Add obstacles to blocked
        for coord in shoot_coords:
            if coord in self.__map.get_obstacles():
                blocked.append(coord)
                d = Hex.distance(tank.get_position(), coord)
                (dx, dy, dz) = ((x - coord.q) / d, (y - coord.r) / d, (z - coord.s) / d)
                for i in range(tank.get_max_range() - d):
                    blocked.append(Hex(coord.q - (i + 1) * dx, coord.r - (i + 1) * dy, coord.s - (i + 1) * dz))

        # Add to blocked my tanks that are not in 1st ring and neutral (if in 1st ring add whole line)
        for t in self.__map.get_tanks().values():
            coord = t.get_position()
            if t.get_player_id() == tank.get_player_id() and Hex.distance(coord, tank.get_position()) > 1:
                blocked.append(coord)
            elif self.__neutrality_check(tank, t):
                if Hex.distance(coord, tank.get_position()) == 1:
                    blocked.append(coord)
                    (dx, dy, dz) = ((x - coord.q), (y - coord.r), (z - coord.s))
                    for i in range(tank.get_max_range()):
                        blocked.append(Hex(x - (i + 1) * dx, y - (i + 1) * dy, z - (i + 1) * dz))
                else:
                    blocked.append(t.get_position())

        # Keep only coords that are not blocked
        shoot_coords = [coord for coord in shoot_coords if coord not in blocked]

        # Enemy tanks
        enemy_tanks = []

        # Add enemy tanks to list
        for t in self.__map.get_tanks().values():
            if t.get_player_id() != tank.get_player_id() and not self.__neutrality_check(tank, t):
                enemy_tanks.append(t)

        # Only keep enemies that are in shoot range whose hp is > 0 and sort them based on hp
        enemy_tanks = [t for t in enemy_tanks if t.get_position() in shoot_coords and t.get_hp() > 0]
        enemy_tanks.sort(key=lambda tt: tt)

        # If there are enemy tanks shoot in line where tank with the lowest hp is
        if enemy_tanks:
            tank_shot = enemy_tanks[0]
        else:
            return None, None

        # List of tanks being shot
        tanks_shot_at = []

        # Add to tanks_shot_at
        coord = tank_shot.get_position()
        d = Hex.distance(tank.get_position(), coord)
        (dx, dy, dz) = ((x - coord.q) / d, (y - coord.r) / d, (z - coord.s) / d)
        for i in range(tank.get_max_range()):
            new_hex = Hex(x - (i + 1) * dx, y - (i + 1) * dy, z - (i + 1) * dz)
            if new_hex in shoot_coords:
                for t in enemy_tanks:
                    if new_hex == t.get_position():
                        tanks_shot_at.append(self.__tank_from_hex(new_hex))

        return Hex(x - dx, y - dy, z - dz), tanks_shot_at

    def __shoot_coords(self, tank: Tank) -> list[Hex]:
        # coords based on center of map
        general_shoot_coords = []
        for radius in range(tank.get_min_range(), tank.get_max_range() + 1):
            general_shoot_coords += Hex.hex_ring(Hex(0, 0, 0), radius)

        # if at_spg keep only straight lines
        if tank.get_type() == "at_spg":
            general_shoot_coords = [coord for coord in general_shoot_coords if 0 in coord]

        # get positional coord based on current tank position and remove those that are not in map
        x, y, z = tank.get_position()
        positional_shoot_coords = [Hex(x + dx, y + dy, z + dz) for (dx, dy, dz) in general_shoot_coords
                                   if not self.__offTheGridDetection(Hex(x + dx, y + dy, z + dz))]

        return positional_shoot_coords

    def __neutrality_check(self, tank_1: Tank, tank_2: Tank) -> bool:
        id1, id2 = tank_1.get_player_id(), tank_2.get_player_id()
        id3 = self.__third_player(id1, id2)
        if id1 in self.__map.get_shoot_actions()[id2] or id2 not in self.__map.get_shoot_actions()[id3]:
            return False
        else:
            return True

    def __third_player(self, id1: int, id2: int) -> int:
        for p in self.__map.get_players():
            if p.id != id1 and p.id != id2:
                return p.id

    def reset_shoot_actions(self, player_id: int) -> None:
        self.__map.get_shoot_actions()[player_id] = []

    def is_in_base(self, tank_pos: Hex) -> bool:
        return tank_pos in self.__map.get_base()

    # Detects if the given coordinates are off the grid
    def __offTheGridDetection(self, h: Hex) -> bool:
        if h in self.__map.get_map().keys():
            return False
        return True

    def __tank_from_hex(self, h: Hex) -> Tank:
        return self.__map.get_tanks()[self.__get_key_from_value(self.__map.get_tank_positions(), h)[0]]

    @staticmethod
    def __get_key_from_value(d: dict, value: Any) -> list[Any]:
        return [k for k, v in d.items() if v == value]
