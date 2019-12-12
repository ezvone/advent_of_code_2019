import re
import pathlib


def read_lines(filename):
    path = pathlib.Path(__file__).parent / filename
    with path.open('rt') as f:
        for line in f:
            yield line.strip('\n')


def read_one_line(filename):
    return next(read_lines(filename))


def read_comma_separated_integers(filename):
    return [int(x) for x in read_one_line(filename).split(',')]


def read_orbits(filename):
    for line in read_lines(filename):
        yield line.split(')')


def _read_direction_line(line):
    for segment in line.split(','):
        direction = segment[0]
        counter = int(segment[1:])
        for _i in range(counter):
            yield direction


def read_directions_per_line(filename):
    for line in read_lines(filename):
        yield list(_read_direction_line(line))


def read_asteroid_map(filename):
    for y, line in enumerate(read_lines(filename)):
        for x, ch in enumerate(line):
            if ch == '#':
                yield (x, y)


def read_moons(filename):
    regex = re.compile(r'<x=(?P<x>-?\d+), y=(?P<y>-?\d+), z=(?P<z>-?\d+)>')
    for line in read_lines(filename):
        m = regex.match(line)
        yield int(m.group('x')), int(m.group('y')), int(m.group('z'))
