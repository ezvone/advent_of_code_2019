from itertools import chain, product, count


from input_reader import read_comma_separated_integers
from intcode import Intcode


class TractorBeamTester:
    def __init__(self, max_coord):
        self.opcodes = read_comma_separated_integers('day19input.txt')
        self.max_coord = max_coord
        self.cache = {}

    def test_coordinates(self, x, y):
        if (x, y) not in self.cache:
            self.cache[x, y] = self._test_coordinates(x, y)
        return self.cache[x, y]

    def _test_coordinates(self, x, y):
        assert 0 <= x <= self.max_coord
        assert 0 <= y <= self.max_coord

        ic = Intcode(self.opcodes)
        ic.start()
        ic.write_input(x)
        ic.write_input(y)
        return {1: True, 0: False}[ic.read_output()]

    def get_first_y(self, x, expected_value, start_y=0, max_error=3):
        y = max(0, min(start_y, self.max_coord))
        min_y = max(0, y // max_error - 1)
        max_y = min(self.max_coord, max(y * max_error + 1, y + max_error + 1))
        start_value = self.test_coordinates(x, y)
        if start_value == expected_value:
            while y > min_y:
                if self.test_coordinates(x, y - 1)  != expected_value:
                    return y
                y -= 1
            return min_y
        else:
            while y < max_y:
                y += 1
                if self.test_coordinates(x, y)  == expected_value:
                    return y
            return None


def puzzle1():
    tester = TractorBeamTester(50)

    x_sweep = ((x, 49) for x in range(49, -1, -1))
    y_sweep = ((49, y) for y in range(50))
    sweep = chain(y_sweep, x_sweep)

    test_run = [(x, y) for x, y in sweep if tester.test_coordinates(x, y)]

    first_ray_x, first_ray_y = test_run[0]
    last_ray_x, last_ray_y = test_run[-1]

    total_count = 0
    for x in range(first_ray_x+1):
        first_y = tester.get_first_y(x, True, first_ray_y * x // first_ray_x - 1)
        if first_y is None:
            continue
        last_y = tester.get_first_y(x, False, last_ray_y * x // last_ray_x + 1)
        if last_y is None:
            last_y = 50
        total_count += last_y - first_y

    return total_count


def bisect(low, high, test):
    assert high > low
    assert not test(low)
    assert test(high)
    if high - low == 1:
        return high
    mid = (high + low) // 2
    if test(mid):
        return bisect(low, mid, test)
    else:
        return bisect(mid, high, test)


def find_first(test, step=3):
    x = 1
    while not test(x):
        x *= step

    return bisect(x // step, x, test)


def puzzle2():
    tester = TractorBeamTester(float('inf'))

    x_sweep = ((x, 49) for x in range(49, -1, -1))
    y_sweep = ((49, y) for y in range(50))
    sweep = chain(y_sweep, x_sweep)

    test_run = [(x, y) for x, y in sweep if tester.test_coordinates(x, y)]

    first_ray_x, first_ray_y = test_run[0]
    last_ray_x, last_ray_y = test_run[-1]

    def test(x):
        last_y = tester.get_first_y(x, False, last_ray_y * x // last_ray_x + 1)

        if last_y < 100:
            return False

        if tester.test_coordinates(x + 99, last_y - 100):
            return True

    rtn_x = find_first(test)
    rtn_y = tester.get_first_y(rtn_x, False, last_ray_y * rtn_x // last_ray_x + 1) - 100

    return 10000 * rtn_x + rtn_y


if __name__ == "__main__":
    assert puzzle1() == 226
    assert puzzle2() == 7900946
    print('OK.')

