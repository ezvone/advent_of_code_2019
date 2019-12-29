from typing import Union, Iterable, Tuple, List, Dict

import re
import pathlib


class TestInput:
    def __init__(self, contents):
        self.contents = contents


FilenameOrTestInput = Union[str, TestInput]
Coord2D = Tuple[int, int]
Coord3D = Tuple[int, int, int]


def read_lines(filename : FilenameOrTestInput) -> Iterable[str]:
    if isinstance(filename, TestInput):
        yield from filename.contents.splitlines()
        return

    path = pathlib.Path(__file__).parent / filename
    with path.open('rt') as f:
        for line in f:
            yield line.strip('\n')


def read_one_line(filename : FilenameOrTestInput) -> str:
    return next(read_lines(filename))


def read_comma_separated_integers(filename : FilenameOrTestInput) -> Iterable[int]:
    return [int(x) for x in read_one_line(filename).split(',')]


def read_orbits(filename : FilenameOrTestInput) -> Iterable[Tuple[str, str]]:
    for line in read_lines(filename):
        yield line.split(')')


def _read_direction_line(line : str) -> Iterable[str]:
    for segment in line.split(','):
        direction = segment[0]
        counter = int(segment[1:])
        for _i in range(counter):
            yield direction


def read_directions_per_line(filename : FilenameOrTestInput) -> Iterable[List[str]]:
    for line in read_lines(filename):
        yield list(_read_direction_line(line))


def read_asteroid_map(filename : FilenameOrTestInput) -> Iterable[Coord2D]:
    for y, line in enumerate(read_lines(filename)):
        for x, ch in enumerate(line):
            if ch == '#':
                yield (x, y)


def read_moons(filename : FilenameOrTestInput) -> Iterable[Coord3D]:
    regex = re.compile(r'<x=(?P<x>-?\d+), y=(?P<y>-?\d+), z=(?P<z>-?\d+)>')
    for line in read_lines(filename):
        m = regex.match(line)
        yield int(m.group('x')), int(m.group('y')), int(m.group('z'))


def read_nanofactory_specs(filename : FilenameOrTestInput
                           ) -> Iterable[Tuple[List[Tuple[int, str]], Tuple[int, str]]]:
    for line in read_lines(filename):
        # 7 A, 1 D => 1 E
        arrow = line.find('=>')
        inputs = [input.split()
            for input in line[:arrow].split(',')]
        out_amount, out_name = line[arrow + len('=>'):].split()
        converted_in = [(int(amount), name) for amount, name in inputs]
        converted_out = int(out_amount), out_name
        yield converted_in, converted_out


def read_labyrinth(filename : FilenameOrTestInput) -> Dict[Coord2D, str]:
    rtn = {}
    start = None
    for y, line in enumerate(read_lines(filename)):
        line = line.rstrip()
        for x, ch in enumerate(line):
            rtn[x, y] = ch
    return rtn


def read_digits(filename : FilenameOrTestInput) -> Iterable[int]:
    line = read_one_line(filename)
    return (int(x) for x in line)
