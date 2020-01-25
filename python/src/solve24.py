from itertools import chain

from input_reader import read_bugs_coordinates


class Bugs:
    def __init__(self, bugs_coordinates):
        self.bugs_coordinates = frozenset(bugs_coordinates)

    def count_neighbouring_bugs(self, coord):
        return sum(
            1 for n in self.iter_neighbours(coord)
            if n in self.bugs_coordinates)

    def calculate_next_value(self, coord):
        if coord in self.bugs_coordinates:
            return self.count_neighbouring_bugs(coord) == 1
        else:
            return self.count_neighbouring_bugs(coord) in (1, 2)

    def copy(self):
        return type(self)(self.bugs_coordinates)

    def step(self):
        all_coords = set(chain(
            *(self.iter_neighbours(c) for c in self.bugs_coordinates))
            ) | self.bugs_coordinates

        self.bugs_coordinates = frozenset(
            coord for coord in all_coords
            if self.calculate_next_value(coord))


class SingleLevelBugs(Bugs):
    def iter_neighbours(self, coord):
        x, y = coord

        if x != 0:
            yield x - 1, y

        if x != 4:
            yield x + 1, y

        if y != 0:
            yield x, y - 1

        if y != 4:
            yield x, y + 1

    def __str__(self):
        return '\n'.join(
            ''.join('#' if (x, y) in self.bugs_coordinates else '_' for x in range(5))
            for y in range(5)
        )

    def __eq__(self, other):
        return self.bugs_coordinates == other.bugs_coordinates

    def __hash__(self):
        return hash(self.bugs_coordinates)

    @property
    def biodiversity_rating(self):
        bit_value = 1
        rtn = 0
        for y in range(5):
            for x in range(5):
                if (x, y) in self.bugs_coordinates:
                    rtn += bit_value
                bit_value *= 2
        return rtn


class MultiLevelBugs(Bugs):

    def iter_neighbours(self, coord):
        level, x, y = coord

        if x == 0:
            yield level - 1, 1, 2
            yield level, x + 1, y
        elif x == 4:
            yield level - 1, 3, 2
            yield level, x - 1, y
        elif x == 1 and y == 2:
            yield level, x - 1, y
            for yy in range(5):
                yield level + 1, 0, yy
        elif x == 3 and y == 2:
            yield level, x + 1, y
            for yy in range(5):
                yield level + 1, 4, yy
        else:
            yield level, x - 1, y
            yield level, x + 1, y

        if y == 0:
            yield level - 1, 2, 1
            yield level, x, y + 1
        elif y == 4:
            yield level - 1, 2, 3
            yield level, x, y - 1
        elif x == 2 and y == 1:
            yield level, x, y - 1
            for xx in range(5):
                yield level + 1, xx, 0
        elif x == 2 and y == 3:
            yield level, x, y + 1
            for xx in range(5):
                yield level + 1, xx, 4
        else:
            yield level, x, y - 1
            yield level, x, y + 1

    def __str__(self):
        levels = set(l for l, x, y in self.bugs_coordinates)

        bugs = {level: SingleLevelBugs({
                    (x,y) for l,x,y in self.bugs_coordinates
                    if l == level})
                for level in levels}

        def field_str(level, x, y):
            if x == y == 2:
                return '?'
            elif (level, x, y) in self.bugs_coordinates:
                return '#'
            else:
                return '_'

        def level_str(level):
            return '\n'.join(
                ''.join(field_str(level, x, y) for x in range(5))
                for y in range(5))

        return '\n\n'.join(f'Level {level}:\n{level_str(level)}'
                           for level in sorted(levels))

    @property
    def number_of_bugs(self):
        return len(self.bugs_coordinates)


def puzzle1():
    bugs = SingleLevelBugs(read_bugs_coordinates('day24input.txt'))

    seen = set()
    while bugs not in seen:
        seen.add(bugs)
        bugs = bugs.copy()
        bugs.step()

    return bugs.biodiversity_rating


def puzzle2():
    bugs = MultiLevelBugs((0, x, y)
                          for x, y in read_bugs_coordinates('day24input.txt'))

    for i in range(200):
        bugs.step()

    return bugs.number_of_bugs


if __name__ == "__main__":
    assert puzzle1() == 28772955
    assert puzzle2() == 2023
    print('OK.')
