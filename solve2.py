from input_reader import read_comma_separated_integers
from intcode import Intcode


class GravityAssistProgram:
    def __init__(self):
        self._codes = read_comma_separated_integers('day2input.txt')

    def run(self, noun, verb):
        c = Intcode(self._codes)
        c.opcodes[1] = noun
        c.opcodes[2] = verb
        c.run()
        return c.opcodes[0]


def puzzle1():
    p = GravityAssistProgram()
    return p.run(12, 2)


def find_result(result_value):
    p = GravityAssistProgram()

    for noun in range(0, 100):
        for verb in range(0, 100):
            if p.run(noun, verb) == result_value:
                return noun, verb


def puzzle2():
    noun, verb = find_result(19690720)
    return 100 * noun + verb


if __name__ == '__main__':
    assert puzzle1() == 6568671
    assert puzzle2() == 3951
    print('OK.')
