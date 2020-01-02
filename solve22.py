from input_reader import read_shuffle_algorithm, TestInput


class DealIntoNewStack:
    def __init__(self, num_cards):
        self.num_cards = num_cards

    def get_next_index(self, previous_index):
        return self.num_cards - previous_index - 1

    def get_previous_index(self, next_index):
        return (-next_index - 1) % self.num_cards


class Cut:
    def __init__(self, num_cards, n):
        self.num_cards = num_cards
        self.n = n

    def get_next_index(self, previous_index):
        return (previous_index - self.n) % self.num_cards

    def get_previous_index(self, next_index):
        return (next_index + self.n) % self.num_cards


class DealWithIncrement:
    def __init__(self, num_cards, step):
        self.num_cards = num_cards
        self.step = step
        self.xstep = pow(self.step, -1, self.num_cards)

    def get_next_index(self, previous_index):
        return (self.step * previous_index) % self.num_cards

    def get_previous_index(self, next_index):
        return (self.xstep * next_index) % self.num_cards


class Shuffler:
    def __init__(self, num_cards):
        self.num_cards = num_cards
        self.definition = list(read_shuffle_algorithm('day22input.txt'))
        self.techniques = [
            self._get_technique(num_cards, technique_name, n)
            for technique_name, n in self.definition]

    @staticmethod
    def _get_technique(num_cards, technique_name, n):
        if technique_name == 'deal into new stack':
            return DealIntoNewStack(num_cards)
        elif technique_name == 'cut':
            return Cut(num_cards, n)
        elif technique_name == 'deal with increment':
            return DealWithIncrement(num_cards, n)
        else:
            raise Exception(f'Unknown techinque name {technique_name}')

    def shuffle(self):
        deck = list(range(self.num_cards))
        for technique in self.techniques:
            deck = [deck[technique.get_previous_index(i)]
                    for i in range(self.num_cards)]
        return deck

    def track_one_card(self, card_index):
        for technique in self.techniques:
            card_index = technique.get_next_index(card_index)
        return card_index

    def back_track_one_card(self, card_index):
        for technique in reversed(self.techniques):
            card_index = technique.get_previous_index(card_index)
        return card_index


def puzzle1():
    shuffler = Shuffler(10007)
    return shuffler.track_one_card(2019)



if __name__ == "__main__":
    assert puzzle1() == 1252
