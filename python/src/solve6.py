from input_reader import read_orbits


class TreeOfOrbits:
    @staticmethod
    def read_orbit_tree_mapping(filename):
        centers = {}
        for center, satellite in read_orbits(filename):
            assert satellite not in centers
            centers[satellite] = center
        return TreeOfOrbits(centers)

    def __init__(self, tree_dict):
        self._tree = tree_dict

    def get_path_to_center(self, obj):
        if obj in self._tree:
            return [obj] + self.get_path_to_center(self._tree[obj])
        else:
            return [obj]

    def get_orbital_distance(self, obj1, obj2):
        path1 = self.get_path_to_center(obj1)
        if obj2 in path1:
            return path1.index(obj2)
        path2 = self.get_path_to_center(obj2)
        if obj1 in path2:
            return path2.index(obj1)

        for i, x in enumerate(path1):
            for j, y in enumerate(path2):
                if x == y:
                    return i + j

    def __iter__(self):
        return iter(self._tree)


def puzzle1():
    tree = TreeOfOrbits.read_orbit_tree_mapping('day6input.txt')
    return sum(len(tree.get_path_to_center(obj)) - 1 for obj in tree)


def puzzle2():
    tree = TreeOfOrbits.read_orbit_tree_mapping('day6input.txt')
    return tree.get_orbital_distance('YOU', 'SAN') - 2


if __name__ == "__main__":
    assert puzzle1() == 144909
    assert puzzle2() == 259
    print('OK.')
