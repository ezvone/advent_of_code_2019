from typing import Optional, Iterable, Tuple
from itertools import chain, count
from math import inf

from input_reader import read_labyrinth, TestInput
from labyrinth import (
    find_all_distances, AreaMap, Coordinate, MapObject, DistanceGraphBase,
    SymmetricalGraphMixin)


def iter_neightbouring_coordinates(x, y):
    yield (x + 1, y)
    yield (x - 1, y)
    yield (x, y + 1)
    yield (x, y - 1)


def detect_portals(raw_lab : dict):
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    portals_by_coord = {}
    for (x, y), ch in raw_lab.items():
        if ch in LETTERS:
            for nx, ny in iter_neightbouring_coordinates(x, y):
                nch = raw_lab.get((nx, ny), ' ')
                if nch in LETTERS:
                    neighbour = nx, nx, nch
                    break
            else:
                assert False, f"invalid portal @ {x}, {y}"
            nx, nx, nch = neighbour
            two = sorted([(x, y, ch), (nx, ny, nch)])
            portal_name = two[0][2] + two[1][2]

            portal_coord, = [
                xy for xy in chain(
                    iter_neightbouring_coordinates(x, y),
                    iter_neightbouring_coordinates(nx, ny))
                if raw_lab.get(xy) == '.']
            portals_by_coord[portal_coord] = portal_name

        else:
            assert ch in ' #.'

    portals_by_name = {}
    for xy, name in portals_by_coord.items():
        portals_by_name.setdefault(name, [])
        portals_by_name[name].append(Coordinate(*xy))
    return portals_by_name


def parse_input():
    raw_lab = read_labyrinth('day20input.txt')
    portals = detect_portals(raw_lab)
    area = AreaMap({
        Coordinate(*xy): MapObject.EMPTY if ch == '.' else MapObject.WALL
        for xy, ch in raw_lab.items()})

    return area, portals


def create_distance_graph(area, portals):
    relevant_coordintes = [c for coords in portals.values() for c in coords]
    graph = find_all_distances(area, relevant_coordintes)

    start_pos, = portals.pop('AA')
    end_pos, = portals.pop('ZZ')
    for coord1, coord2 in portals.values():
        graph[coord1].add_neighbour(graph[coord2], 1)

    return graph, start_pos, end_pos


def puzzle1():
    area, portals = parse_input()
    graph, start_pos, end_pos = create_distance_graph(area, portals)
    return graph.find_shortest_path_two_ways(graph[start_pos], graph[end_pos])


def detect_outer_portals_coordinates(portals):
    coords = [c for coords in portals.values() for c in coords]
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    outer_xs = min(xs), max(xs)
    outer_ys = min(ys), max(ys)

    outer_coords = [c for c in coords if c.x in outer_xs or c.y in outer_ys]

    VERIFY = True
    if VERIFY:
        inner_coords = set(coords) - set(outer_coords)
        xs2 = [c.x for c in inner_coords]
        ys2 = [c.y for c in inner_coords]
        inner_xs = min(xs2), max(xs2)
        inner_ys = min(ys2), max(ys2)
        assert all(c.x in inner_xs or c.y in inner_ys for c in inner_coords)

    return outer_coords


class RecursiveMazeNode:
    def __init__(self, coord, level):
        self.coord = coord
        self.level = level

    def __repr__(self):
        return f'<RMNode {self.coord} @ {self.level}>'

    def _data(self):
        return self.level, self.coord

    def __hash__(self):
        return hash(self._data())

    def __eq__(self, other):
        return self._data() == other._data()


class RecursiveMaze(SymmetricalGraphMixin, DistanceGraphBase):

    TOPMOST_LEVEL = 1

    def __init__(self, level_graph, portals, outer_coords, endpoints):
        self.level_graph = level_graph
        self.portals_down = {}
        self.portals_up = {}
        for coord1, coord2 in portals.values():
            if coord1 in outer_coords:
                assert coord2 not in outer_coords
                self.portals_down[coord2] = coord1
                self.portals_up[coord1] = coord2
            else:
                assert coord2 in outer_coords
                self.portals_down[coord1] = coord2
                self.portals_up[coord2] = coord1

        self.outer_coords = set(outer_coords)

    def iter_neighbouring_nodes(self, node : RecursiveMazeNode
                               ) -> Iterable[Tuple[RecursiveMazeNode, int]]:

        coord = node.coord
        level = node.level

        neighbours = self.level_graph[coord].neighbours.items()

        for neighbour_node, distance in neighbours:
            yield RecursiveMazeNode(neighbour_node.identifier, level), distance

        if None is not (n := self.portals_down.get(coord)):
            yield RecursiveMazeNode(n, level+1), 1
        if node.level != RecursiveMaze.TOPMOST_LEVEL:
            if None is not (n := self.portals_up.get(coord)):
                yield RecursiveMazeNode(n, level-1), 1


def puzzle2():
    area, portals = parse_input()
    outer_portals_coordinates = detect_outer_portals_coordinates(portals)

    relevant_coordintes = [c for coords in portals.values() for c in coords]
    graph = find_all_distances(area, relevant_coordintes)

    start_pos, = portals.pop('AA')
    end_pos, = portals.pop('ZZ')

    maze = RecursiveMaze(graph, portals, outer_portals_coordinates,
                         [start_pos, end_pos])

    start_node = RecursiveMazeNode(start_pos, RecursiveMaze.TOPMOST_LEVEL)
    end_node = RecursiveMazeNode(end_pos, RecursiveMaze.TOPMOST_LEVEL)

    return maze.find_shortest_path_two_ways(start_node, end_node)


if __name__ == "__main__":
    assert puzzle1() == 620
    assert puzzle2() == 7366
    print('OK.')
