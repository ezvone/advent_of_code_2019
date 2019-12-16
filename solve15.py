from enum import Enum

from intcode import IntcodeRunner
from input_reader import read_comma_separated_integers


class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

    def move_coord(self, x, y):
        return {
            Direction.NORTH: (x, y - 1),
            Direction.SOUTH: (x, y + 1),
            Direction.EAST:  (x + 1, y),
            Direction.WEST:  (x - 1, y)
        }[self]

    def back(self):
        return {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST:  Direction.WEST,
            Direction.WEST:  Direction.EAST
        }[self]


class Status(Enum):
    WALL = 0
    MOVED = 1
    FOUND = 2


class MapObject(Enum):
    UNKNOWN = 1
    EMPTY = 2
    WALL = 3
    OXYGEN_SYSTEM = 4


class AreaMap(dict):
    def __init__(self):
        super().__init__()
        self.distances = {}

    def __getitem__(self, coord):
        return self.get(coord, MapObject.UNKNOWN)

    def get_available_directions(self, x, y):
        for direction in Direction:
            if self[direction.move_coord(x, y)] != MapObject.WALL:
                yield direction

    def get_locations(self, map_object):
        return [coord for coord, obj in self.items() if obj == map_object]


class DroidRemote:
    def __init__(self):
        self.ic = IntcodeRunner(read_comma_separated_integers('day15input.txt'))

    def move(self, direction):
        self.ic.communicate(direction.value)
        return Status(self.ic.communicate())


class FakeDroid:
    def __init__(self, area_map, initial_coord):
        self.area_map = area_map
        self.coord = initial_coord

    def move(self, direction):
        next_coord = direction.move_coord(*self.coord)
        assert self.area_map[next_coord] != MapObject.UNKNOWN
        if self.area_map[next_coord] == MapObject.WALL:
            return Status.WALL
        else:
            self.coord = next_coord
            if self.area_map[next_coord] == MapObject.OXYGEN_SYSTEM:
                return Status.FOUND
            else:
                return Status.MOVED


def explore_depth_first(coord, area, droid, distance):
    directions = list(area.get_available_directions(*coord))
    for direction in directions:
        next_coord = direction.move_coord(*coord)
        if area[next_coord] == MapObject.WALL:
            continue
        if area[next_coord] != MapObject.UNKNOWN:
            if area.distances[next_coord] <= distance + 1:
                continue
        status = droid.move(direction)
        area.distances[next_coord] = distance + 1
        if status == Status.WALL:
            area[next_coord] = MapObject.WALL
        else:
            if status == Status.FOUND:
                area[next_coord] = MapObject.OXYGEN_SYSTEM
            else:
                area[next_coord] = MapObject.EMPTY
            explore_depth_first(next_coord, area, droid, distance + 1)
            droid.move(direction.back())


def puzzle1():
    droid = DroidRemote()
    area = AreaMap()
    coord = (0, 0)
    area[coord] = MapObject.EMPTY
    area.distances[coord] = 0
    explore_depth_first(coord, area, droid, 0)
    oxygen_coord, = area.get_locations(MapObject.OXYGEN_SYSTEM)
    return area.distances[oxygen_coord]


def puzzle2():
    droid = DroidRemote()
    area = AreaMap()
    coord = (0, 0)
    area[coord] = MapObject.EMPTY
    area.distances[coord] = 0
    explore_depth_first(coord, area, droid, 0)
    oxygen_coord, = area.get_locations(MapObject.OXYGEN_SYSTEM)

    fake_droid = FakeDroid(area, oxygen_coord)
    area = AreaMap()
    area[oxygen_coord] = MapObject.OXYGEN_SYSTEM
    area.distances[oxygen_coord] = 0
    explore_depth_first(oxygen_coord, area, fake_droid, 0)

    return max(
        distance for coord, distance in area.distances.items()
        if area[coord] == MapObject.EMPTY)


if __name__ == "__main__":
    assert puzzle1() == 240
    assert puzzle2() == 322
    print('OK.')
