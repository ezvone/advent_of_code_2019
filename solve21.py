from input_reader import read_comma_separated_integers
from intcode import Intcode


class SpringDroidProgrammer:
    def __init__(self):
        self.ic = Intcode(read_comma_separated_integers('day21input.txt'))
        self.ic.start()

    def read_prompt(self):
        rtn = ''
        ch = self.ic.read_output()
        while ch != 10:
            rtn += chr(ch)
            ch = self.ic.read_output()
        return rtn

    def write_command(self, command):
        for ch in command:
            self.ic.write_input(ord(ch))
        self.ic.write_input(10)

    def read_output(self):
        while not self.ic.finished:
            ch = self.ic.read_output()
            if ch < 256:
                pass
            else:
                return ch

    def program(self, source):
        self.read_prompt()
        for line in source.splitlines():
            if sline := line.strip():
                self.write_command(' '.join(sline.split()))


def puzzle1():
    programmer = SpringDroidProgrammer()
    programmer.program('''
    NOT A J
    NOT B T
    OR T J
    NOT C T
    OR T J
    AND D J
    WALK
    ''')
    return programmer.read_output()


def puzzle2():
    programmer = SpringDroidProgrammer()
    programmer.program('''
    NOT	G	T
    NOT	F	J
    OR	T	J
    OR	E	J
    NOT	C	T
    AND	T	J
    NOT	B	T
    OR	T	J
    NOT	H	T
    NOT	T	T
    OR	E	T
    AND	T	J
    AND	D	J
    NOT	A	T
    OR	T	J
    RUN
    ''')
    return programmer.read_output()


if __name__ == "__main__":
    assert puzzle1() == 19353074
    assert puzzle2() == 1147582556
    print('OK.')

