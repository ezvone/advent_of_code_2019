from itertools import count
import numpy as np

from input_reader import read_digits


base_pluses = np.array([False, True, False, False])
base_minuses = np.array([False, False, False, True])


def get_patterns(n, length):
    tile_n = length // (4 * n) + 1

    pluses = np.tile(np.repeat(base_pluses, n), tile_n)[1 : length + 1]
    minuses = np.tile(np.repeat(base_minuses, n), tile_n)[1 : length + 1]
    return pluses, minuses


def calculate_fft_phase(input):
    length = len(input)
    dts = np.zeros(4)
    iter_patterns = (get_patterns(i, length) for i in range(1, length+1))
    return np.fromiter((abs(input[pluses].sum() - input[minuses].sum()) % 10
                        for pluses, minuses in iter_patterns), dtype=np.int64)


def puzzle1():
    signal = np.fromiter(read_digits('day16input.txt'), dtype=np.int64)
    for i in range(100):
        signal = calculate_fft_phase(signal)
    return ''.join(str(x) for x in signal[:8])


def calculate_sub_fft_phase(input):
    return np.cumsum(input[::-1])[::-1]


def puzzle2():
    from input_reader import TestInput

    input = np.fromiter(read_digits('day16input.txt'), dtype=np.int64)
    offset = (input[:7] * np.fromiter((10**i for i in range(6, -1, -1)), dtype=np.int64)).sum()
    signal = np.tile(input, 10_000)
    if offset > len(signal) // 2:
        subsignal = signal[offset:]
        for i in range(100):
            subsignal = calculate_sub_fft_phase(subsignal)
            subsignal %= 10
        return ''.join(str(x) for x in subsignal[:8])
    else:
        print('Slow mode... this could take a year or two...')
        for i in range(100):
            print(i)
            signal = calculate_fft_phase(signal)
        return ''.join(str(x) for x in signal[offset:offset+8])


if __name__ == "__main__":
    assert puzzle1() == '29795507'
    assert puzzle2() == '89568529'
    print('OK.')
