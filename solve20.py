from typing import Optional
from itertools import chain

from input_reader import read_labyrinth, TestInput
from labyrinth import find_all_distances, AreaMap, Coordinate, MapObject


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
    shortest_path, shortest_distance = graph.find_shortest_path(
        graph[start_pos], graph[end_pos])
    return shortest_distance


if __name__ == "__main__":
    assert puzzle1() == 620
    print('Part 1 OK.')
