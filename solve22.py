from input_reader import read_shuffle_algorithm, TestInput


class Technique:
    def __init__(self, modulo, factor=1, addend=0):
        self.factor = factor
        self.addend = addend
        self.modulo = modulo

    def calculate(self, x):
        return (self.factor * x + self.addend) % self.modulo

    def inverse(self):
        inv_factor = pow(self.factor, -1, self.modulo)
        return Technique(self.modulo, inv_factor, -self.addend*inv_factor)

    def chain(self, t2):
        if self.modulo != t2.modulo:
            raise ValueError("Only techniques with the same modulo can be chained")

        return Technique(
            self.modulo,
            self.factor * t2.factor % self.modulo,
            (self.addend * t2.factor + t2.addend) % self.modulo)

    def pow(self, n):
        assert n >= 1
        if n == 1:
            return self

        squared = Technique(self.modulo,
                            pow(self.factor, 2, self.modulo),
                            (self.factor + 1) * self.addend % self.modulo)
        if n % 2 == 0:
            return squared.pow(n // 2)
        else:
            return squared.pow(n // 2).chain(self)


class Shuffler:
    def __init__(self, num_cards, repetitions=1):
        self.num_cards = num_cards
        self.definition = list(read_shuffle_algorithm('day22input.txt'))
        self.technique = Technique(self.num_cards)
        for technique_name, n in self.definition:
            technique = self._get_technique(num_cards, technique_name, n)
            self.technique = self.technique.chain(technique)

        self.technique = self.technique.pow(repetitions)

    @staticmethod
    def _get_technique(num_cards, technique_name, n):
        if technique_name == 'deal into new stack':
            return Technique(num_cards, -1, -1)
        elif technique_name == 'cut':
            return Technique(num_cards, 1, -n)
        elif technique_name == 'deal with increment':
            return Technique(num_cards, n, 0)
        else:
            raise Exception(f'Unknown techinque name {technique_name}')

    def track_one_card(self, card_index):
        return self.technique.calculate(card_index)

    def back_track_one_card(self, card_index):
        return self.technique.inverse().calculate(card_index)


def puzzle1():
    shuffler = Shuffler(10007)
    return shuffler.track_one_card(2019)


def puzzle2():
    shuffler = Shuffler(119315717514047, 101741582076661)
    return shuffler.back_track_one_card(2020)


if __name__ == "__main__":
    assert puzzle1() == 1252
    assert puzzle2() == 46116012647793
    print('OK.')
