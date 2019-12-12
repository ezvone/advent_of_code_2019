from itertools import permutations

from intcode import IntcodeRunner
from input_reader import read_comma_separated_integers


class Amplifier(IntcodeRunner):
    def __init__(self, phase_setting):
        super().__init__(read_comma_separated_integers('day7input.txt'))
        self.communicate(phase_setting)

    def run(self, input_value):
        self.communicate(input_value)
        return self.communicate()


def get_amplification_circuit_thruster_value(phase_settings):
    amplifiers = [Amplifier(phase_setting) for phase_setting in phase_settings]
    value = 0
    thruster_value = None
    while True:
        for amplifier in amplifiers:
            value = amplifier.run(value)
            if amplifier.finished:
                return thruster_value
        thruster_value = value


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
