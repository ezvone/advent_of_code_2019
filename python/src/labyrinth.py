from typing import Iterable, Dict, Tuple, Any, Set, Union, List
from enum import Enum
from math import inf
from itertools import count


Number = Union[int, float]


class Coordinate:
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f'<Coordinate {self.x}, {self.y}>'

    def _data(self) -> Tuple[int, int]:
        return self.x, self.y

    def __iter__(self) -> Iterable[int]:
        return iter(self._data())

    def __eq__(self, other) -> bool:
        return self._data() == other._data()

    def __hash__(self) -> int:
        return hash(self._data())

    def up(self) -> 'Coordinate':
        return Coordinate(self.x, self.y - 1)

    def down(self) -> 'Coordinate':
        return Coordinate(self.x, self.y + 1)

    def left(self) -> 'Coordinate':
        return Coordinate(self.x - 1, self.y)

    def right(self) -> 'Coordinate':
        return Coordinate(self.x + 1, self.y)


class Direction(Enum):
    NORTH = 'N'
    SOUTH = 'S'
    WEST = 'W'
    EAST = 'E'

    def move_coord(self, coord : Coordinate) -> Coordinate:
        return {
            Direction.NORTH: coord.up,
            Direction.SOUTH: coord.down,
            Direction.WEST: coord.left,
            Direction.EAST: coord.right,
        }[self]()

    def opposite(self) -> 'Direction':
        return {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST:  Direction.WEST,
            Direction.WEST:  Direction.EAST
        }[self]


class MapObject(Enum):
    EMPTY = '.'
    WALL = '#'
    TARGET = '$'


class AreaMap:
    def __init__(self, data : Dict[Coordinate, MapObject] = None):
        self.data = {} if data is None else data.copy()

    def copy(self) -> 'AreaMap':
        return AreaMap(self.data.copy())

    def peek(self, coord : Coordinate, *, default=None) -> MapObject:
        if coord in self.data:
            return self.data[coord]
        return default

    def __getitem__(self, coord : Coordinate) -> MapObject:
        assert isinstance(coord, Coordinate)
        return self.peek(coord, default=MapObject.WALL)

    def __setitem__(self, coord : Coordinate, value : MapObject):
        assert isinstance(coord, Coordinate)
        self.data[coord] = value

    def __iter__(self) -> Iterable[Coordinate]:
        return iter(self.data)

    def get_target_locations(self) -> Iterable[Coordinate]:
        return [coord for coord in self if self[coord] == MapObject.TARGET]

    def __str__(self):
        xs, ys = map(set, zip(*self))
        minx = min(xs)
        maxx = max(xs)
        miny = min(ys)
        maxy = max(ys)
        return '\n'.join(
            ''.join(self[Coordinate(x, y)].value
                    if Coordinate(x, y) in self
                    else ' '
                    for x in range(minx, maxx + 1))
            for y in range(miny, maxy + 1))


def find_distances(area : AreaMap, start_coord : Coordinate) -> Dict[Coordinate, int]:
    distance = 0
    rtn = {start_coord : distance}
    leaf_coordinates = [start_coord]

    while leaf_coordinates:
        next_leaves = []
        for coord in leaf_coordinates:
            if area[coord] == MapObject.TARGET:
                continue
            for next_coord in [d.move_coord(coord) for d in Direction]:
                if next_coord in rtn:
                    continue
                if area[next_coord] == MapObject.WALL:
                    continue
                next_leaves.append(next_coord)
        distance += 1
        for leaf in next_leaves:
            rtn[leaf] = distance
        leaf_coordinates = next_leaves
    return rtn


class DistanceGraphBase:

    def iter_neighbouring_nodes(self, n) -> Iterable[Tuple[Any, Number]]:
        raise NotImplementedError

    def find_shortest_path(self, node1 : Any, node2 : Any,
                           distance_limit : Number = inf
                           ) -> Tuple[List, Number]:
        return self._find_shortest_path(node1, node2, set(), distance_limit)

    def _find_shortest_path(self, node1 : Any, node2 : Any,
                            forbidden_nodes : Set, distance_limit : Number
                            ) -> Tuple[List, Number]:
        forbidden2 = forbidden_nodes | {node1}
        best_path = []
        best_distance = distance_limit

        neighbours = list(self.iter_neighbouring_nodes(node1))
        for n, d in neighbours:
            if n in forbidden_nodes:
                continue
            if d >= best_distance:
                continue
            if n == node2:
                subpath, subdistance = [], 0
            else:
                subpath, subdistance = self._find_shortest_path(
                    n, node2, forbidden2, best_distance - d)

            if d + subdistance < best_distance:
                best_path = [n] + subpath
                best_distance = d + subdistance

        return best_path, best_distance


class SymmetricalGraphMixin(DistanceGraphBase):

    def find_shortest_path_two_ways(self, node1 : Any, node2 : Any):
        explore1 = self._explore_iteratively(node1)
        explore2 = self._explore_iteratively(node2)
        while True:
            explored1 = next(explore1)
            explored2 = next(explore2)
            overlap = set(explored1).intersection(explored2)
            if overlap:
                best = min(overlap, key=lambda n: explored1[n]+explored2[n])
                distance = explored1[best] + explored2[best]
                return distance

    def _explore_iteratively(self, start_node : Any):
        explored_nodes = {start_node: 0}
        finished_nodes = set()
        for i in count(1):
            max_distance = 50 * i
            if finished_nodes.issuperset(explored_nodes):
                break
            for node, d in list(explored_nodes.items()):
                if node not in finished_nodes:
                    self._explore(node, explored_nodes, finished_nodes,
                                  d, max_distance)
            yield explored_nodes

    def _explore(self, node : Any,
                 explored_nodes : Dict[Any, int],
                 finished_nodes : Set[Any],
                 current_distance : int = 0,
                 max_distance : Number = inf):
        finished = True
        for n2, d in self.iter_neighbouring_nodes(node):
            total_distance = current_distance + d
            if total_distance > max_distance:
                finished = False
                continue
            if explored_nodes.get(n2, inf) <= total_distance:
                continue
            explored_nodes[n2] = total_distance
            self._explore(n2, explored_nodes, finished_nodes, total_distance, max_distance)
        if finished:
            finished_nodes.add(node)


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


class DistanceGraph(SymmetricalGraphMixin, DistanceGraphBase):
    _nodes : Dict[Any, DistanceGraphNode]

    def __init__(self):
        self._nodes = {}

    def __bool__(self):
        return bool(self._nodes)

    def __iter__(self):
        return iter(self._nodes)

    def iter_neighbouring_nodes(self, n):
        return n.neighbours.items()

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
