from math import atan2, pi
from collections import defaultdict

from input_reader import read_asteroid_map


def get_distance(coords1, coords2):
    x1, y1 = coords1
    x2, y2 = coords2
    return ((x2-x1)**2 + (y2-y1)**2) ** 0.5


def get_angle(coords1, coords2):
    x1, y1 = coords1
    x2, y2 = coords2
    return atan2(y2-y1, x2-x1)


def count_visible_asteroids(coords, all_coords):
    angles = {get_angle(coords, coords2)
              for coords2 in all_coords
              if coords != coords2}
    return len(angles)


def puzzle1():
    all_coords = list(read_asteroid_map('day10input.txt'))
    return max(count_visible_asteroids(coords, all_coords)
               for coords in all_coords)


def get_vaporization_order(all_asteroid_coords, station_coords):
    coords_by_angle = defaultdict(list)
    for c in all_asteroid_coords:
        if c != station_coords:
            coords_by_angle[get_angle(c, station_coords)].append(c)
    for coords_in_line in coords_by_angle.values():
        coords_in_line.sort(key=lambda c: get_distance(station_coords, c))
    angle_order = sorted(coords_by_angle, key=lambda alpha: (alpha-pi/2+2*pi) % (2*pi))
    vaporization_order = []
    while any(coords_by_angle.values()):
        for angle in angle_order:
            if coords_by_angle[angle]:
                vaporization_order.append(coords_by_angle[angle].pop(0))
    return vaporization_order


def puzzle2():
    all_coords = list(read_asteroid_map('day10input.txt'))
    station_coords = max(all_coords,
        key=lambda coords: count_visible_asteroids(coords, all_coords))
    assert count_visible_asteroids(station_coords, all_coords) == 292

    vaporization_order = get_vaporization_order(all_coords, station_coords)
    x, y = vaporization_order[199]
    return 100 * x + y


if __name__ == "__main__":
    assert puzzle1() == 292
    assert puzzle2() == 317
    print('OK.')
