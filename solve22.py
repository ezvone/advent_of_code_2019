import numpy as np

from input_reader import read_shuffle_algorithm, TestInput


class Shuffler:
    def __init__(self):
        self.algorithm = list(read_shuffle_algorithm('day22input.txt'))

    @staticmethod
    def reverse(deck, _ignored=None):
        return deck[::-1]

    @staticmethod
    def cut(deck, n):
        return np.concatenate([deck[n:], deck[:n]])

    @staticmethod
    def deal(deck, step):
        indices = np.arange(0, step * deck.size, step) % deck.size
        return deck[np.lexsort((indices,))]

    @staticmethod
    def apply_technique(technique_name, deck, n):
        func = {
            'reverse': Shuffler.reverse,
            'cut': Shuffler.cut,
            'deal': Shuffler.deal,
        }[technique_name]
        return func(deck, n)

    def shuffle(self, num_cards=10007):
        deck = np.arange(num_cards)
        for technique, n in self.algorithm:
            deck = self.apply_technique(technique, deck, n)
        return deck


def puzzle1():
    shuffler = Shuffler()
    deck = shuffler.shuffle()
    return np.where(deck == 2019)[0][0]


if __name__ == "__main__":
    assert puzzle1() == 1252
