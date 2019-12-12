from input_reader import read_comma_separated_integers
from intcode import Intcode


class EmergencyHulPaintingProgram:

    DIRECTIONS = (0,1), (1,0), (0,-1), (-1,0)  # up, right, down, left

    def __init__(self, hul: dict):
        ic = Intcode(read_comma_separated_integers('day11input.txt'))
        self.run_gen = ic.run_generator()
        next(self.run_gen)

        self.hul = hul
        self.position = 0, 0
        self.direction_index = 0

    def _read_value(self):
        while True:
            value = self.run_gen.send(self.hul.get(self.position, 0))
            if value is not None:
                return value

    def _rotate(self, value):
        rotation = 1 if value else -1
        self.direction_index = (self.direction_index + rotation) % 4
        x, y = self.position
        dx, dy = self.DIRECTIONS[self.direction_index]
        self.position = x + dx, y + dy

    def paint(self):
        while True:
            try:
                color = self._read_value()
                self.hul[self.position] = color
                rotation = self._read_value()
                self._rotate(rotation)
            except StopIteration:
                return


def puzzle1():
    hul = {}
    robot = EmergencyHulPaintingProgram(hul)
    robot.paint()
    return len(hul)


def print_hul(hul):
    minx = min(coord[0] for coord in hul)
    maxx = max(coord[0] for coord in hul)
    miny = min(coord[1] for coord in hul)
    maxy = max(coord[1] for coord in hul)

    return '\n'.join(
        ''.join('#' if hul.get((x, y)) else ' ' for x in range(minx, maxx + 1))
        for y in range(maxy, miny - 1, -1))


def puzzle2():
    hul = {(0, 0): 1}
    robot = EmergencyHulPaintingProgram(hul)
    robot.paint()
    return print_hul(hul)


if __name__ == "__main__":
    assert puzzle1() == 1863
    solution2 = puzzle2()
    assert solution2 == ' ###  #    #  # #    ####   ## #    ####   \n #  # #    #  # #       #    # #       #   \n ###  #    #  # #      #     # #      #    \n #  # #    #  # #     #      # #     #     \n #  # #    #  # #    #    #  # #    #      \n ###  ####  ##  #### ####  ##  #### ####   '
    print(solution2)
    print('OK.')
