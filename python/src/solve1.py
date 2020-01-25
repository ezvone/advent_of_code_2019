
from input_reader import read_lines


def get_required_fuel(mass):
    return mass // 3 - 2


def get_total_required_fuel(mass):
    if (required_fuel := get_required_fuel(mass)) < 0:
        return 0

    return required_fuel + get_total_required_fuel(required_fuel)


def puzzle1():
    masses = (int(mass) for mass in read_lines('day1input.txt'))
    return sum(get_required_fuel(mass) for mass in masses)


def puzzle2():
    masses = (int(mass) for mass in read_lines('day1input.txt'))
    return sum(get_total_required_fuel(mass) for mass in masses)


if __name__ == "__main__":
    assert puzzle1() == 3331523
    assert puzzle2() == 4994396
    print('OK.')
