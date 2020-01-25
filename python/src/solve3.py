from input_reader import read_directions_per_line


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.__data() == other.__data()

    def __hash__(self):
        return hash(self.__data())

    def __data(self):
        return (self.x, self.y)

    def next_coord(self, direction):
        dx, dy = {
            'U': (0, 1),
            'D': (0, -1),
            'R': (1, 0),
            'L': (-1, 0)
        }[direction]

        return Coordinate(self.x + dx, self.y + dy)

    def distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)


def get_wire_coordinates(movements, start):
    coord = start
    yield coord
    for direction in movements:
        coord = coord.next_coord(direction)
        yield coord


def puzzle1():
    zero = Coordinate(0,0)
    wire_1_moves, wire_2_moves = read_directions_per_line('day3input.txt')
    wire_1_coords = set(get_wire_coordinates(wire_1_moves, zero))
    wire_2_coords = set(get_wire_coordinates(wire_2_moves, zero))
    intersections = (wire_1_coords & wire_2_coords) - {zero}
    return min(zero.distance(c) for c in intersections)


def puzzle2():
    zero = Coordinate(0,0)
    wire_1_moves, wire_2_moves = read_directions_per_line('day3input.txt')
    wire_1_coords = {}
    for distance, coord in enumerate(get_wire_coordinates(wire_1_moves, zero)):
        wire_1_coords.setdefault(coord, distance)
    wire_2_coords = {}
    for distance, coord in enumerate(get_wire_coordinates(wire_2_moves, zero)):
        wire_2_coords.setdefault(coord, distance)
    intersections = (set(wire_1_coords) & set(wire_2_coords)) - {zero}
    return min(wire_1_coords[c] + wire_2_coords[c] for c in intersections)


if __name__ == "__main__":
    assert puzzle1() == 293
    assert puzzle2() == 27306
    print('OK.')
