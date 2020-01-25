import itertools
from math import gcd

from input_reader import read_moons


class Moon1D:
    def __init__(self, x, v=0):
        self.x = x
        self.v = v

    def __repr__(self):
        return f'<Moon1D {self.x} -> {self.v}>'

    def __eq__(self, other):
        return (self.x == other.x and self.v == other.v)

    def apply_gravity(self, other):
        """apply gravity on *both* moons"""
        if self.x > other.x:
            gravity = -1
        elif self.x < other.x:
            gravity = 1
        else:
            gravity = 0
        self.v += gravity
        other.v -= gravity

    def apply_velocity(self):
        self.x += self.v


class Moons1D:
    def __init__(self, coords):
        self.moons = [Moon1D(coord) for coord in coords]

    def __repr__(self):
        return f'<Moon1D {self.moons!r}>'

    def __eq__(self, other):
        return all(m1 == m2
            for m1, m2 in itertools.zip_longest(self.moons, other.moons))

    def apply_step(self):
        for m1, m2 in itertools.combinations(self.moons, 2):
            m1.apply_gravity(m2)

        for m in self.moons:
            m.apply_velocity()


class Moons3D:
    def __init__(self, list_of_moon_coords):
        xs, ys, zs = zip(*list_of_moon_coords)
        self.dimensions = [Moons1D(dim_coords) for dim_coords in (xs, ys, zs)]

    def apply_step(self):
        for dim in self.dimensions:
            dim.apply_step()

    def get_moons(self):
        coords_by_dim = [
            [moon1d.x for moon1d in dim.moons]
            for dim in self.dimensions]
        coords_by_moon = zip(*coords_by_dim)
        velocities_by_dim = [
            [moon1d.v for moon1d in dim.moons]
            for dim in self.dimensions]
        velocities_by_moon = zip(*velocities_by_dim)

        return zip(coords_by_moon, velocities_by_moon)

    def get_total_energy(self):
        total = 0
        for (x, y, z), (vx, vy, vz) in self.get_moons():
            potential = abs(x) + abs(y) + abs(z)
            kinetic = abs(vx) + abs(vy) + abs(vz)
            total += potential * kinetic
        return total


def puzzle1():
    moons = Moons3D(read_moons('day12input.txt'))
    for _i in range(1000):
        moons.apply_step()
    return moons.get_total_energy()


def get_common_period(*periods):
    rtn = 1
    for p in periods:
        rtn *= p // gcd(rtn, p)
    return rtn


def puzzle2():
    moon_coords = list(read_moons('day12input.txt'))
    xs, ys, zs = zip(*moon_coords)
    initial_moons_dims = [Moons1D(coords) for coords in (xs, ys, zs)]
    moons_dims = [Moons1D(coords) for coords in (xs, ys, zs)]

    dimension_repetition_periods = []
    for moons, init_moons in zip(moons_dims, initial_moons_dims):
        for i in itertools.count(1):
            moons.apply_step()
            if moons == init_moons:
                dimension_repetition_periods.append(i)
                break

    return get_common_period(*dimension_repetition_periods)


if __name__ == "__main__":
    assert puzzle1() == 7471
    assert puzzle2() == 376243355967784
    print('OK.')

