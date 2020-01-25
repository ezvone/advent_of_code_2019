from intcode import Intcode
from input_reader import read_comma_separated_integers


class BoostProgram:
    def __init__(self):
        self.ic = Intcode(read_comma_separated_integers('day9input.txt'))

    def _read_all(self):
        while not self.ic.finished:
            yield self.ic.read_output()

    def run(self, input_value):
        self.ic.start()
        self.ic.write_input(input_value)
        return list(self._read_all())


def puzzle1():
    boost = BoostProgram()
    return boost.run(1)


def puzzle2():
    boost = BoostProgram()
    return boost.run(2)


if __name__ == "__main__":
    assert puzzle1() == [3780860499]
    assert puzzle2() == [33343]
    print('OK.')

