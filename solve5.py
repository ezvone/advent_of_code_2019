from intcode import Intcode
from input_reader import read_comma_separated_integers


class DiagnosticProgram:
    def __init__(self):
        self.ic = Intcode(read_comma_separated_integers('day5input.txt'))

    def run(self, system_id):
        self.ic.start()
        self.ic.write_input(system_id)

        while not self.ic.finished:
            yield self.ic.read_output()


def puzzle1():
    outputs = list(DiagnosticProgram().run(1))
    assert all(x == 0 for x in outputs[:-1])
    return outputs[-1]


def puzzle2():
    output, = DiagnosticProgram().run(5)
    return output


if __name__ == "__main__":
    assert puzzle1() == 3122865
    assert puzzle2() == 773660
    print('OK.')
