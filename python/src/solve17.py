from itertools import product

from input_reader import read_comma_separated_integers
from intcode import Intcode


class AftScaffoldingControlAndInformationInterface:
    def __init__(self, wake_vacuum_robot_up=False):
        opcodes = read_comma_separated_integers('day17input.txt')
        if wake_vacuum_robot_up:
            assert opcodes[0] == 1
            opcodes[0] = 2
        self.ic = Intcode(opcodes)
        self.ic.start()

    def scan_cameras(self):
        line = []
        while True:
            while (ch := self.ic.read_output()) != 10:
                if ch is None:
                    break
                line.append(chr(ch))
            if line:
                yield ''.join(line)
                line = []
            else:
                return

    def provide_routines(self, main_routine, a, b, c, live_video=False):
        assert self.read_line() == 'Main:'
        self.provide_input(main_routine)
        assert self.read_line() == 'Function A:'
        self.provide_input(a)
        assert self.read_line() == 'Function B:'
        self.provide_input(b)
        assert self.read_line() == 'Function C:'
        self.provide_input(c)
        assert self.read_line() == 'Continuous video feed?'
        self.provide_input('y' if live_video else 'n')



    def read_line(self):
        rtn = []
        while (ch := self.ic.read_output()) != 10:
            rtn.append(chr(ch))
        return ''.join(rtn)

    def provide_input(self, s):
        for ch in s:
            self.ic.write_input(ord(ch))
        self.ic.write_input(10)

    def find_intersections(self):
        scaffolds = list(self.scan_cameras())
        width, = {len(line) for line in scaffolds}
        height = len(scaffolds)
        for x, y in product(range(1, width-1), range(1, height-1)):
            if not any(scaffolds[y+j][x+i] == '.'
                       for i, j in ((0, 1), (0, -1), (1, 0), (-1, 0))):
                yield x, y

    def detect_required_movements(self):
        scaffolds = list(self.scan_cameras())
        width, = {len(line) for line in scaffolds}
        height = len(scaffolds)
        (rx, ry), = [
            (x, y) for x, y in product(range(width), range(height))
            if scaffolds[y][x] in '^v<>']
        rd = scaffolds[ry][rx]

        def forward(robot_direction=rd, robot_x=rx, robot_y=ry):
            return {
                '^': (robot_x, robot_y - 1),
                'v': (robot_x, robot_y + 1),
                '<': (robot_x - 1, robot_y),
                '>': (robot_x + 1, robot_y),
            }[robot_direction]

        def left(robot_direction=rd):
            return {
                '^': '<',
                'v': '>',
                '<': 'v',
                '>': '^',
            }[robot_direction]

        def right(robot_direction=rd):
            return {
                '^': '>',
                'v': '<',
                '<': '^',
                '>': 'v',
            }[robot_direction]

        def get(coord):
            x, y = coord
            if 0 <= x < width and 0 <= y < height:
                return scaffolds[y][x] == '#'
            else:
                return False

        while True:
            if get(coord := forward(direction := rd, rx, ry)):
                yield 'F'
            elif get(coord := forward(direction := left(rd), rx, ry)):
                yield 'L'
                yield 'F'
            elif get(coord := forward(direction := right(rd), rx, ry)):
                yield 'R'
                yield 'F'
            else:
                return
            rd = direction
            rx, ry = coord


def _moves_definition(moves):
    moves = moves + 'E'
    p = 0
    while moves[p] != 'E':
        forwards = 0
        while moves[p] == 'F':
            forwards += 1
            p += 1
        if forwards:
            yield str(forwards)
        if moves[p] == 'L':
            yield 'L'
            p += 1
        if moves[p] == 'R':
            yield 'R'
            p += 1


def moves_definition(moves):
    return ','.join(_moves_definition(moves))


def group_moves(moves, p=0, existing_groups=None, main_routine_length=0, max_groups=3, max_definition_size=20):
    if existing_groups is None:
        existing_groups = []

    while any(moves.startswith(grp, p) for grp in existing_groups):
        grp, = [grp for grp in existing_groups if moves.startswith(grp, p)]
        p += len(grp)
        main_routine_length += 1
        if main_routine_length * 2 - 1 > max_definition_size:
            return None

    if p >= len(moves):
        return existing_groups

    if len(existing_groups) >= max_groups:
        return None

    for i in range(1, len(moves) - p):
        grp = moves[p : p + i]
        if any(g.startswith(grp) for g in existing_groups):
            # technically valid, but not likely, and it would complicate code
            continue
        if len(moves_definition(grp)) > max_definition_size:
            return None
        rtn = group_moves(moves, p, existing_groups + [grp], main_routine_length,
                          max_groups, max_definition_size)
        if rtn is not None:
            return rtn

    return None


def puzzle1():
    ascii = AftScaffoldingControlAndInformationInterface()
    return sum(x * y for x, y in ascii.find_intersections())


def caculate_movement_routines(moves):
    groups = dict(zip('ABC', group_moves(moves, max_groups=3)))
    main_routine = []
    while moves:
        for name, grp in groups.items():
            if moves.startswith(grp):
                main_routine.append(name)
                moves = moves[len(grp):]
                break
        else:
            raise AssertionError()
    yield ','.join(main_routine)
    for name in 'ABC':
        yield moves_definition(groups.get(name, []))


def puzzle2():
    ascii = AftScaffoldingControlAndInformationInterface(True)
    moves = ''.join(ascii.detect_required_movements())

    main, a, b, c = [routine for routine in caculate_movement_routines(moves)]
    ascii.provide_routines(main, a, b, c)
    while not ascii.ic.finished:
        ch = ascii.ic.read_output()
        if ch < 256:
            #print(chr(ch), end='')
            pass
        else:
            return ch


if __name__ == "__main__":
    assert puzzle1() == 5940
    assert puzzle2() == 923795
    print('OK.')

