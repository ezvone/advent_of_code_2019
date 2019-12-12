from intcode import Intcode
from input_reader import read_comma_separated_integers


class BoostProgram:
    def __init__(self):
        ic = Intcode(read_comma_separated_integers('day9input.txt'))
        self.gen = ic.run_generator()
        next(self.gen)

    def run(self, input_value):
        self.gen.send(input_value)
        return list(self.gen)


def puzzle1():
    boost = BoostProgram()
    return boost.run(1)


def puzzle2():
    boost = BoostProgram()
    return boost.run(2)


if __name__ == "__main__":
    assert puzzle1() == [3780860499]
    assert puzzle2() == [33343]

