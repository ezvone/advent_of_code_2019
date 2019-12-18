from enum import Enum

from intcode import IntcodeRunner
from input_reader import read_comma_separated_integers
from labyrinth import MapObject, AreaMap, Coordinate, Direction, find_distances



class Status(Enum):
    WALL = 0
    MOVED = 1
    FOUND = 2


class DroidRemote:
    def __init__(self):
        self.ic = IntcodeRunner(read_comma_separated_integers('day15input.txt'))

    def move(self, direction):
        command = {
            Direction.NORTH: 1,
            Direction.SOUTH: 2,
            Direction.WEST: 3,
            Direction.EAST: 4
        }[direction]
        self.ic.communicate(command)
        return Status(self.ic.communicate())


def get_available_directions(area, coord):
    for direction in Direction:
        if area.peek(direction.move_coord(coord)) != MapObject.WALL:
            yield direction


def explore_depth_first(coord, area, droid, distance, distances=None):
    if distances is None:
        distances = {coord: distance}
    directions = list(get_available_directions(area, coord))
    for direction in directions:
        next_coord = direction.move_coord(coord)
        if area.peek(next_coord) == MapObject.WALL:
            continue
        if distances.get(next_coord, float('inf')) <= distance + 1:
            continue
        status = droid.move(direction)
        distances[next_coord] = distance + 1
        if status == Status.WALL:
            area[next_coord] = MapObject.WALL
        else:
            if status == Status.FOUND:
                area[next_coord] = MapObject.TARGET
            else:
                area[next_coord] = MapObject.EMPTY
            explore_depth_first(next_coord, area, droid, distance + 1, distances)
            droid.move(direction.opposite())
    return distances


def puzzle1():
    droid = DroidRemote()
    area = AreaMap()
    coord = Coordinate(0, 0)
    area[coord] = MapObject.EMPTY
    distances = explore_depth_first(coord, area, droid, 0)
    oxygen_coord, = area.get_target_locations()
    return distances[oxygen_coord]


def puzzle2():
    droid = DroidRemote()
    area = AreaMap()
    coord = Coordinate(0, 0)
    area[coord] = MapObject.EMPTY
    explore_depth_first(coord, area, droid, 0)
    oxygen_coord, = area.get_target_locations()

    area[oxygen_coord] = MapObject.EMPTY
    distances = find_distances(area, oxygen_coord)

    return max(distances.values())


if __name__ == "__main__":
    assert puzzle1() == 240
    assert puzzle2() == 322
    print('OK.')
