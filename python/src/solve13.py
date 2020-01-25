from enum import Enum

from intcode import Intcode
from input_reader import read_comma_separated_integers


class TileId(Enum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    HPADDLE = 3
    BALL = 4

    def __str__(self):
        return {
            TileId.EMPTY: ' ',
            TileId.WALL: '#',
            TileId.BLOCK: '%',
            TileId.HPADDLE: '=',
            TileId.BALL: 'o',
        }[self]


class Joystick(Enum):
    NEUTRAL = 0
    LEFT = -1
    RIGHT = 1


class ArcadeCabinet:
    def __init__(self):
        self.ic = Intcode(read_comma_separated_integers('day13input.txt'))
        self.screen = {}
        self.score = 0

    def set_number_of_quarters(self, value):
        self.ic.memory[0] = value

    def read_tile_from_ic(self):
        data = []
        while len(data) < 3 and not self.ic.finished:
            if self.ic.requires_input:
                self.ic.write_input(self.joystick_value)
            else:
                data.append(self.ic.read_output())

        if len(data) == 3:
            return tuple(data)

    def run(self):
        self.ic.start()
        while None is not (tile := self.read_tile_from_ic()):
            x, y, tile_id = tile
            if (x, y) == (-1, 0):
                self.score = tile_id
                continue
            self.screen[(x, y)] = TileId(tile_id)

    @property
    def joystick_value(self):
        ball_coords = [
            k for k, v in self.screen.items()
            if v == TileId.BALL]
        paddle_coords = [
            k for k, v in self.screen.items()
            if v == TileId.HPADDLE]
        if len(ball_coords) == len(paddle_coords) == 1:
            ballx = ball_coords[0][0]
            paddlex = paddle_coords[0][0]
            if ballx < paddlex:
                return Joystick.LEFT.value
            elif ballx > paddlex:
                return Joystick.RIGHT.value
            else:
                return Joystick.NEUTRAL.value


def puzzle1():
    arcade = ArcadeCabinet()
    arcade.run()
    return sum(1 for tile_id in arcade.screen.values()
               if tile_id == TileId.BLOCK)


def puzzle2():
    arcade = ArcadeCabinet()
    arcade.set_number_of_quarters(2)
    print('Playing the game, this may take a while...')
    arcade.run()
    return arcade.score


if __name__ == "__main__":
    assert puzzle1() == 255
    assert puzzle2() == 12338
    print('OK.')
