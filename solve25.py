import re
from itertools import chain
from typing import List, Tuple, Set, Dict
from dataclasses import dataclass

from input_reader import read_comma_separated_integers
from intcode import Intcode


@dataclass
class Room:
    room_name : str
    doors : list
    items : list

    def __hash__(self):
        return hash(self.room_name)

    def __eq__(self, other):
        return self.room_name == other.room_name


class SecurityCheckpointFailed(Exception):
    def __init__(self, too_heavy : bool):
        self.too_heavy = too_heavy


class PasswordFound(Exception):
    def __init__(self, password):
        self.password = password


class Robot:
    def __init__(self):
        self.ic = Intcode(read_comma_separated_integers('day25input.txt'))
        self.ic.start()

    def run_manually(self):
        print(self._read_output(), end='')

        while self.ic.requires_input:
            txt = input()
            self.write_input(f'{txt}\n')
            print(self._read_output(), end='')

    def go(self, direction) -> Room:
        self.write_input(f'{direction}\n')
        return self.read_room_info()

    def take(self, item):
        self.write_input(f'take {item}\n')
        output = self.parse_output()
        assert output['lines'] == [f'You take the {item}.']

    def drop(self, item):
        self.write_input(f'drop {item}\n')
        output = self.parse_output()
        assert output['lines'] == [f'You drop the {item}.']

    def inv(self):
        self.write_input(f'inv\n')
        output = self.parse_output()
        if output['lines'] == ["You aren't carrying any items."]:
            return []
        else:
            return output['Items in your inventory:']

    def write_input(self, s):
        for ch in s:
            self.ic.write_input(ord(ch))

    def _read_output(self):
        rtn = []
        while self.ic.has_output:
            rtn.append(chr(self.ic.read_output()))
        return ''.join(rtn)

    def parse_output(self):
        rtn = { 'lines': [] }
        list_name = None
        end = False
        for line in self._read_output().splitlines():
            assert not end
            if line.endswith(':'):
                assert not list_name
                list_name = line
                rtn[list_name] = []
            elif not line:
                list_name = None
            elif list_name:
                assert line.startswith('- ')
                rtn[list_name].append(line[2:])
            elif line == 'Command?':
                end = True
            else:
                rtn['lines'].append(line)

        return rtn

    def read_room_info(self) -> Room:

        output = self.parse_output()
        lines = output['lines']

        assert lines[0].startswith('== ') and lines[0].endswith(' ==')
        room_name = lines[0][3:-3]
        doors = output.get('Doors here lead:', [])
        items = output.get('Items here:', [])

        TOO_LIGHT = 'A loud, robotic voice says '\
                    '"Alert! Droids on this ship are heavier than the detected value!"'\
                    ' and you are ejected back to the checkpoint.'

        TOO_HEAVY = 'A loud, robotic voice says '\
                    '"Alert! Droids on this ship are lighter than the detected value!"'\
                    ' and you are ejected back to the checkpoint.'

        if TOO_LIGHT in lines:
            raise SecurityCheckpointFailed(False)

        if TOO_HEAVY in lines:
            raise SecurityCheckpointFailed(True)

        for line in lines:
            if m := re.search(
                r'You should be able to get in by typing (\d+) on the keypad', line):
                raise PasswordFound(m.group(1))

        return Room(room_name=room_name,
                    doors=doors, items=items)


def explore_area(robot : Robot,
                 room : Room,
                 direction_back : str,
                 items_to_pick_up : Set[str] = None,
                 checkpoint_handler = None):

    if items_to_pick_up:
        for item in items_to_pick_up.intersection(room.items):
            robot.take(item)

    rtn = {room}

    for direction in room.doors:
        if direction == direction_back:
            continue

        direction_back_from_next = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east'
        }[direction]
        try:
            next_room = robot.go(direction)
            rtn.update(explore_area(robot, next_room,
                       direction_back_from_next, items_to_pick_up,
                       checkpoint_handler))

            back_room = robot.go(direction_back_from_next)
            assert back_room == room
        except SecurityCheckpointFailed:
            if checkpoint_handler:
                next_room = checkpoint_handler(robot, direction)
                rtn.update(explore_area(robot, next_room,
                           direction_back_from_next))
                back_room = robot.go(direction_back_from_next)
                assert back_room == room
            else:
                continue

    return rtn


def try_combinations(robot: Robot, items : Set[str], direction : str):
    try:
        return robot.go(direction)
    except SecurityCheckpointFailed as e:
        if e.too_heavy:
            return None
        else:
            remaining = set(items)
            for item in items:
                robot.take(item)
                sub_result = try_combinations(robot, remaining - {item}, direction)
                if sub_result is None:
                    remaining.remove(item)
                    robot.drop(item)
                else:
                    return sub_result


def make_checkpoint_handler(usable_items):
    def checkpoint_handler(robot, direction) -> Room:
        for item in usable_items:
            robot.drop(item)
        return try_combinations(robot, set(usable_items), direction)

    return checkpoint_handler


def puzzle():
    robot = Robot()
    #robot.run_manually()

    room = robot.read_room_info()
    seen_rooms = explore_area(robot, room, None)

    bad_items = set(['infinite loop', 'photons', 'molten lava',
                     'giant electromagnet', 'escape pod'])

    all_items = set(chain(*(room.items for room in seen_rooms)))
    usable_items = all_items - bad_items
    explore_area(robot, room, None, usable_items)

    try:
        explore_area(robot, room, None, None, make_checkpoint_handler(usable_items))
    except PasswordFound as ex:
        return ex.password


if __name__ == "__main__":
    assert puzzle() == '278664'
    print('OK.')
