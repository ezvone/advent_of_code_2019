from input_reader import read_one_line


class SpaceImageFormat:
    def __init__(self, width, height, data):
        assert len(data) % (width * height) == 0
        self.w, self.h = width, height
        number_of_layers = len(data) // (width * height)
        self.layers = [self._read_layer(data, i)
                       for i in range(number_of_layers)]

    def _read_layer(self, data, layer_number):
        start = self.w * self.h * layer_number
        return data[start : start + self.w * self.h]

    def overlay_layers(self):
        def overlay_pixel(values):
            for value in values:
                if value in '01':
                    return value
            return '2'

        rtn = [overlay_pixel(values)
               for values in zip(*self.layers)]
        assert len(rtn) == self.w * self.h
        return rtn

    def print_layer(self, layer):
        mapping = ' #?'
        def print_row(row):
            return ''.join(mapping[int(chr)] for chr in row)
        rows = [layer[i * self.w : (i + 1) * self.w] for i in range(self.h)]
        return '\n'.join(print_row(row) for row in rows)


def puzzle1():
    data = read_one_line('day8input.txt').strip()
    image = SpaceImageFormat(25, 6, data)
    least_zeroes_layer = min(image.layers,
                             key=lambda lay: sum(1 for ch in lay if ch == '0'))
    ones = sum(1 for ch in least_zeroes_layer if ch == '1')
    twos = sum(1 for ch in least_zeroes_layer if ch == '2')
    return ones * twos


def puzzle2():
    data = read_one_line('day8input.txt').strip()
    image = SpaceImageFormat(25, 6, data)
    overlayed = image.overlay_layers()
    return image.print_layer(overlayed)


if __name__ == "__main__":
    assert puzzle1() == 1441
    solution2 = puzzle2()
    assert solution2 == '###  #  # #### ###  ###  \n#  # #  #    # #  # #  # \n#  # #  #   #  ###  #  # \n###  #  #  #   #  # ###  \n# #  #  # #    #  # #    \n#  #  ##  #### ###  #    '
    print(solution2)
    print('OK.')
