import heapq
import random
from typing import Optional, Any

from src.constants import optimal_hexes
from src.map.game_map import Map
from src.map.hex import Hex
from src.vehicles.tank import Tank


class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, Any]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: Any, priority: float) -> None:
        heapq.heappush(self.elements, (priority, item))

    def get(self) -> Any:
        return heapq.heappop(self.elements)[1]


# move-shoot logic
class MSLogic:

    def __init__(self, game_map: Map):
        self.__map = game_map

    def move(self, start: Hex, tank: Tank) -> Hex:
        visited = []
        rings = [[start]]
        for k in range(1, tank.sp + 1):
            rings.append([])
            for h in rings[k - 1]:
                for direction in range(6):
                    neighbor = Hex.hex_neighbor(h, direction)
                    if neighbor not in visited and neighbor not in self.__map.obstacles \
                            and not self.__offTheGridDetection(neighbor):
                        visited.append(neighbor)
                        rings[k].append(neighbor)

        visited = [h for h in visited if h not in self.__map.spawn
                   and h not in self.__map.tank_positions.values()]
        visited.sort(key=lambda x: x)

        move_to = []
        if visited:
            if visited[0] == Hex(0, 0, 0):
                d = Hex.distance(Hex(0, 0, 0), visited[1])
            else:
                d = Hex.distance(Hex(0, 0, 0), visited[0])
            move_to = [h for h in visited if Hex.distance(Hex(0, 0, 0), h) == d]
            for h in move_to:
                if abs(h) == optimal_hexes[tank.type] and\
                       not self.can_be_shot(tank.player_id, h).keys():
                    return h

        return random.choice(move_to) if visited else None

    def shoot(self, tank: Tank) -> tuple[Optional[Hex], Optional[list[Tank]]]:
        if tank.type != "at_spg":
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
            if coord in self.__map.obstacles:
                blocked.append(coord)

        # Add to blocked my and neutral tanks
        for t in self.__map.tanks.values():
            if t.player_id == tank.player_id or self.__neutrality_check(tank, t):
                blocked.append(t.position)

        # Enemy tanks
        enemy_tanks = []

        # Add enemy tanks to list
        for t in self.__map.tanks.values():
            if t.position not in blocked:
                enemy_tanks.append(t.position)

        # Keep only coords that are not blocked and in enemy_tanks
        shoot_coords = [coord for coord in shoot_coords if coord not in blocked and coord in enemy_tanks]

        # From hex list make tank list
        tank_shoot_coords = [self.__tank_from_hex(h) for h in shoot_coords]

        # Keep tanks whose hp is > 0 and sort them based on hp and cp
        tank_shoot_coords = [t for t in tank_shoot_coords if t.hp > 0]
        tank_shoot_coords.sort(key=lambda tt: tt)
        sorted(tank_shoot_coords, key=lambda tankk: tankk.cp, reverse=True)  # sort by capture points

        # Shoot at tank with the biggest cp and lowest hp
        if tank_shoot_coords:
            return tank_shoot_coords[0].position, [tank_shoot_coords[0]]
        else:
            return None, None

    def __straight_trajectory(self, tank: Tank) -> tuple[Optional[Hex], Optional[list[Tank]]]:
        # Shoot coords based on tank position
        shoot_coords = self.__shoot_coords(tank)
        x, y, z = tank.position

        # Blocked hexes
        blocked = []

        # Add obstacles to blocked
        for coord in shoot_coords:
            if coord in self.__map.obstacles:
                blocked.append(coord)
                d = Hex.distance(tank.position, coord)
                (dx, dy, dz) = ((x - coord.q) / d, (y - coord.r) / d, (z - coord.s) / d)
                for i in range(tank.max_range - d):
                    blocked.append(Hex(coord.q - (i + 1) * dx, coord.r - (i + 1) * dy, coord.s - (i + 1) * dz))

        # Add to blocked my tanks that are not in 1st ring and neutral (if in 1st ring add whole line)
        for t in self.__map.tanks.values():
            coord = t.position
            if t.player_id == tank.player_id and Hex.distance(coord, tank.position) > 1:
                blocked.append(coord)
            elif self.__neutrality_check(tank, t):
                if Hex.distance(coord, tank.position) == 1:
                    blocked.append(coord)
                    (dx, dy, dz) = ((x - coord.q), (y - coord.r), (z - coord.s))
                    for i in range(tank.max_range):
                        blocked.append(Hex(x - (i + 1) * dx, y - (i + 1) * dy, z - (i + 1) * dz))
                else:
                    blocked.append(t.position)

        # Keep only coords that are not blocked
        shoot_coords = [coord for coord in shoot_coords if coord not in blocked]

        # Enemy tanks
        enemy_tanks = []

        # Add enemy tanks to list
        for t in self.__map.tanks.values():
            if t.player_id != tank.player_id and not self.__neutrality_check(tank, t):
                enemy_tanks.append(t)

        # Only keep enemies that are in shoot range whose hp is > 0 and sort them based on hp
        enemy_tanks = [t for t in enemy_tanks if t.position in shoot_coords and t.hp > 0]
        enemy_tanks.sort(key=lambda tt: tt)
        sorted(enemy_tanks, key=lambda tankk: tankk.cp, reverse=True)  # sort by capture points

        # If there are enemy tanks shoot in line where tank with the lowest hp is
        if enemy_tanks:
            tank_shot = enemy_tanks[0]
        else:
            return None, None

        # List of tanks being shot
        tanks_shot_at = []

        # Add to tanks_shot_at
        coord = tank_shot.position
        d = Hex.distance(tank.position, coord)
        (dx, dy, dz) = ((x - coord.q) / d, (y - coord.r) / d, (z - coord.s) / d)
        for i in range(tank.max_range):
            new_hex = Hex(x - (i + 1) * dx, y - (i + 1) * dy, z - (i + 1) * dz)
            if new_hex in shoot_coords:
                for t in enemy_tanks:
                    if new_hex == t.position:
                        tanks_shot_at.append(self.__tank_from_hex(new_hex))

        return Hex(x - dx, y - dy, z - dz), tanks_shot_at

    def __shoot_coords(self, tank: Tank) -> list[Hex]:
        # coords based on center of map
        general_shoot_coords = []
        for radius in range(tank.min_range, tank.max_range + 1):
            general_shoot_coords += Hex.hex_ring(Hex(0, 0, 0), radius)

        # if at_spg keep only straight lines
        if tank.type == "at_spg":
            general_shoot_coords = [coord for coord in general_shoot_coords if 0 in coord]

        # get positional coord based on current tank position and remove those that are not in map
        x, y, z = tank.position
        positional_shoot_coords = [Hex(x + dx, y + dy, z + dz) for (dx, dy, dz) in general_shoot_coords
                                   if not self.__offTheGridDetection(Hex(x + dx, y + dy, z + dz))]

        return positional_shoot_coords

    def __neutrality_check(self, tank_1: Tank, tank_2: Tank) -> bool:
        id1, id2 = tank_1.player_id, tank_2.player_id
        id3 = self.__third_player(id1, id2)
        if id1 in self.__map.shoot_actions[id2] or id2 not in self.__map.shoot_actions[id3]:
            return False
        else:
            return True

    def __third_player(self, id1: int, id2: int) -> int:
        for p in self.__map.players:
            if p.id != id1 and p.id != id2:
                return p.id

    def reset_shoot_actions(self, player_id: int) -> None:
        self.__map.shoot_actions[player_id] = []

    def is_in_base(self, tank_pos: Hex) -> bool:
        return tank_pos in self.__map.base

    # Detects if the given coordinates are off the grid
    def __offTheGridDetection(self, h: Hex) -> bool:
        if h in self.__map.map.keys():
            return False
        return True

    def __tank_from_hex(self, h: Hex) -> Tank:
        return self.__map.tanks[self.__get_key_from_value(self.__map.tank_positions, h)[0]]

    @staticmethod
    def __get_key_from_value(d: dict, value: Any) -> list[Any]:
        return [k for k, v in d.items() if v == value]

    def a_star(self, start: Hex, finish: Hex):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from: dict[Hex, [Hex]] = {}
        cost_so_far: dict[Hex, float] = {start: 0}
        came_from[start] = None

        while not frontier.empty():
            current: Hex = frontier.get()
            if current == finish:
                break

            for next_coord in self.__hexNeighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_coord not in cost_so_far or new_cost < cost_so_far[next_coord]:
                    cost_so_far[next_coord] = new_cost
                    priority = new_cost + Hex.distance(next_coord, finish)
                    frontier.put(next_coord, priority)
                    came_from[next_coord] = current

        path = []
        current = finish
        while current != start:
            path.append(current)
            if current not in came_from:
                return None
            current = came_from[current]
        path.append(start)
        path.reverse()
        path.pop(0)  # remove hex we stand on

        return path

    def __hexNeighbors(self, h: Hex) -> [Hex]:
        neighbors = []
        for direction in range(6):
            new_neighbor = Hex.hex_neighbor(h, direction)
            if not self.__offTheGridDetection(new_neighbor) and not (new_neighbor in self.__map.obstacles):
                neighbors.append(new_neighbor)
        return neighbors

    def can_be_shot(self, player_id: int, hex: Hex) -> dict[bool, int]:
        times = 0
        for t in self.__map.tanks.values():
            if player_id == t.player_id:
                # if tanks belong to the same player - skip
                continue
            # assume that if we go into the range, enemy tank will automatically shoot us
            if t.max_range < Hex.distance(t.position, hex) or\
                    Hex.distance(t.position, hex) < t.min_range:
                # if this t cannot shoot our tank - skip
                continue
            else:
                times += 1
        if times != 0:
            return {True: times}
        else:
            return {False: times}
