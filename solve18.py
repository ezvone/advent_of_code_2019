from typing import (
    Tuple, FrozenSet, Optional, Dict, Iterator,
    Union, Callable, Iterable, Any)
from math import inf
from functools import wraps
from itertools import combinations
from collections import defaultdict

from input_reader import read_labyrinth, TestInput
from labyrinth import find_distances, AreaMap, Coordinate, MapObject

Number = Union[int, float]


KEY_CHARS =  'abcdefghijklmnopqrstuvwxyz'
DOOR_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
KEY_TO_DOOR_CHAR = dict(zip(KEY_CHARS, DOOR_CHARS))


class DistanceGraphNode:
    def __init__(self, identifier):
        self.identifier = identifier
        self.neighbours = {}
        self.data = None

    def __repr__(self):
        return f'<Node {self.identifier}>'

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        return self.identifier == other.identifier

    def add_neighbour(self, node, distance):
        assert node not in self.neighbours
        self.neighbours[node] = distance
        node.neighbours[self] = distance


class DistanceGraph:
    _nodes : Dict[Any, DistanceGraphNode]

    def __init__(self):
        self._nodes = {}

    def __bool__(self):
        return bool(self._nodes)

    def __iter__(self):
        return iter(self._nodes)

    def copy(self):
        rtn = DistanceGraph()
        for identifier, node in self._nodes.items():
            rtn[identifier].data = node.data
            for neighbour, distance in node.neighbours.items():
                rtn[identifier].neighbours[rtn[neighbour.identifier]] = distance
        return rtn

    def __getitem__(self, identifier) -> DistanceGraphNode:
        if identifier not in self._nodes:
            self._nodes[identifier] = DistanceGraphNode(identifier)
        return self._nodes[identifier]


class ConnectionToNode:
    def __init__(self, node_id, obatacle_ids : Iterable, distance : int):
        self.node_id = node_id
        self.obatacle_ids = set(obatacle_ids)
        self.distance = distance


class DistanceGraphWithObstacles:
    _nodes : Dict[Any, Iterable[ConnectionToNode]]

    def __init__(self, distance_graph : DistanceGraph, is_obstacle):
        self._nodes = {}
        for identifier in distance_graph:
            if is_obstacle(identifier):
                continue
            node = distance_graph[identifier]

            seen = {identifier}
            finder = self._find_neighbours(distance_graph, is_obstacle, node, seen)
            for distance, neighbour_id, obstacles in finder:
                connection = ConnectionToNode(neighbour_id, obstacles, distance)
                self._nodes.setdefault(identifier, [])
                self._nodes[identifier].append(connection)

    @classmethod
    def _find_neighbours(cls, graph, is_obstacle, node, seen):
        for neighbour, distance in node.neighbours.items():
            ident = neighbour.identifier
            if ident in seen:
                continue
            seen = seen | {ident}
            if not is_obstacle(ident):
                yield distance, ident, set()
            next_finder = cls._find_neighbours(
                graph, is_obstacle, neighbour, seen)
            for d2, id2, obstacles in next_finder:
                yield distance + d2, id2, {ident} | obstacles

    def get_available_directions(self, node_id, removed_obstacles
                                 ) -> Dict[Any, int]:
        rtn = {}
        for connection in self._nodes[node_id]:
            if connection.obatacle_ids.issubset(removed_obstacles):
                if connection.node_id in removed_obstacles:
                    continue
                rtn[connection.node_id] = min(
                    rtn.get(connection.node_id, inf), connection.distance)
        return rtn



def read_area_map(override_input : Optional[TestInput] = None
                  ) -> Tuple[AreaMap, FrozenSet[Coordinate],
                             Dict[Coordinate, Coordinate], Coordinate]:
    input_map = read_labyrinth(override_input or 'day18input.txt')

    keys = {ch: (x, y) for (x, y), ch in input_map.items()
            if ch in KEY_CHARS}
    doors = {ch: (x, y) for (x, y), ch in input_map.items()
            if ch in DOOR_CHARS}

    key_to_door_coords = {
        Coordinate(x, y): Coordinate(*doors[KEY_TO_DOOR_CHAR[key_ch]])
        for key_ch, (x, y) in keys.items()
        if KEY_TO_DOOR_CHAR[key_ch] in doors
        }

    starting_position, = [Coordinate(x, y) for (x, y), ch in input_map.items()
                          if ch == '@']

    def get_map_object(x, y, ch):
        if (x, y) in keys.values():
            return MapObject.EMPTY
        elif (x, y) in doors.values():
            return MapObject.EMPTY
        else:
            return {
                '#': MapObject.WALL,
                '.': MapObject.EMPTY,
                '@': MapObject.EMPTY
            }[ch]

    area = AreaMap({Coordinate(x, y): get_map_object(x, y, ch)
                    for (x, y), ch in input_map.items()})

    for door_x_y in doors.values():
        if Coordinate(*door_x_y) not in key_to_door_coords.values():
            # A door which does not open is like a wall
            area[Coordinate(*door_x_y)] = MapObject.WALL

    key_coords = frozenset(Coordinate(x, y) for x, y in keys.values())

    return area, key_coords, key_to_door_coords, starting_position


def find_all_distances(area : AreaMap, relevant_coordinates : Iterable[Coordinate]
                       ) -> DistanceGraph:
    coords = set(relevant_coordinates)

    seen = set()
    graph = DistanceGraph()

    for coord in coords:
        area2 = area.copy()
        for coord2 in coords:
            if coord != coord2:
                area2[coord2] = MapObject.TARGET

        distances = find_distances(area2, coord)

        for coord2 in coords:
            if coord != coord2:
                c1c2 = frozenset([coord, coord2])
                if c1c2 not in seen:
                    seen.add(c1c2)
                    if coord2 in distances:
                        graph[coord].add_neighbour(graph[coord2], distances[coord2])

    return graph


def find_possible_actions(
        area : AreaMap, position : Coordinate,
        closed_door_coords : FrozenSet[Coordinate],
        key_coords : FrozenSet[Coordinate]
        ) -> Iterator[Tuple[int, Coordinate]]:
    """Find all possible actions at current position, an action being move to a next key.

    Yield (distance, next_key_coord) tuples.
    """
    for key_coord in key_coords:
        distance = find_distance(area, position, key_coord, closed_door_coords, key_coords)
        if distance is not None:
            yield distance, key_coord


class FastestSolutionFinder:
    def __init__(self,
                 graph : DistanceGraphWithObstacles,
                 key_to_door_coords : Dict[Coordinate, Coordinate]):
        self.graph = graph
        self.key_to_door_coords = key_to_door_coords
        self.cache = {}

    def find_shortest_solution(self,
                            starting_positions : Tuple[Coordinate],
                            removed_obstacles : Optional[frozenset] = None,
                            limit : Number = inf
                            ) -> Number:

        if (starting_positions, removed_obstacles) in self.cache:
            cached_result, cached_limit = self.cache[starting_positions, removed_obstacles]
            if cached_result >= cached_limit:
                if limit <= cached_limit:
                    return cached_result
            else:
                return cached_result

        best_found_distance = limit
        if not removed_obstacles:
            removed_obstacles = frozenset(starting_positions)

        available_directions = [
            (pos1, pos2, distance)
            for pos1 in starting_positions
            for pos2, distance in self.graph.get_available_directions(
                                    pos1, removed_obstacles).items()
            ]

        if not available_directions:
            return 0

        for position1, position2, distance in available_directions:
            if distance > best_found_distance:
                continue

            removed_obstacles2 = removed_obstacles | {
                position2, self.key_to_door_coords.get(position2)}

            starting_positions2 = tuple(
                p if p != position1 else position2
                for p in starting_positions
            )

            d = distance + self.find_shortest_solution(
                starting_positions2, removed_obstacles2,
                best_found_distance - distance)

            if d < best_found_distance:
                best_found_distance = d

        self.cache[starting_positions, removed_obstacles] = best_found_distance, limit
        return best_found_distance


def solve_puzzle(multiple_entrances=False):
    area, key_coords, key_to_door_coords, starting_position = read_area_map()

    if multiple_entrances:
        starting_positions = (
            starting_position.up().left(),
            starting_position.down().left(),
            starting_position.up().right(),
            starting_position.down().right())
        area[starting_position] = MapObject.WALL
        area[starting_position.up()] = MapObject.WALL
        area[starting_position.down()] = MapObject.WALL
        area[starting_position.left()] = MapObject.WALL
        area[starting_position.right()] = MapObject.WALL
    else:
        starting_positions = (starting_position,)

    relevant_coordinates = list(key_coords) + list(key_to_door_coords.values()) + list(starting_positions)
    distances_graph = find_all_distances(area, relevant_coordinates)

    door_coords = set(key_to_door_coords.values())
    def is_obstacle(coord):
        return coord in door_coords
    distances_graph_with_obstacles = DistanceGraphWithObstacles(distances_graph, is_obstacle)

    solution_finder = FastestSolutionFinder(
        distances_graph_with_obstacles, key_to_door_coords)

    return solution_finder.find_shortest_solution(starting_positions)


def puzzle1():
    return solve_puzzle()


def puzzle2():
    return solve_puzzle(True)


if __name__ == "__main__":
    assert puzzle1() == 4900
    assert puzzle2() == 2462
    print('OK.')


