from itertools import permutations

from intcode import Intcode
from input_reader import read_comma_separated_integers


class Amplifier:
    def __init__(self, phase_setting):
        self.ic = Intcode(read_comma_separated_integers('day7input.txt'))
        self.ic.start()
        self.ic.write_input(phase_setting)

    def run(self, input_value):
        self.ic.write_input(input_value)
        return self.ic.read_output()

    @property
    def finished(self):
        return self.ic.finished


def get_amplification_circuit_thruster_value(phase_settings):
    amplifiers = [Amplifier(phase_setting) for phase_setting in phase_settings]
    value = 0
    thruster_value = None
    while True:
        for amplifier in amplifiers:
            value = amplifier.run(value)
        thruster_value = value
        if amplifier.finished:
            return thruster_value


def find_max_thrust(phase_settings_pool):
    return max(
        get_amplification_circuit_thruster_value(phase_settings)
        for phase_settings in permutations(phase_settings_pool))


def puzzle1():
    return find_max_thrust([0,1,2,3,4])


def puzzle2():
    return find_max_thrust([5,6,7,8,9])


if __name__ == "__main__":
    assert puzzle1() == 46014
    assert puzzle2() == 19581200
    print('OK.')
