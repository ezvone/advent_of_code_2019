from input_reader import read_comma_separated_integers
from intcode import IntcodeRunner


class SpringDroidProgrammer:
    def __init__(self):
        self.ic = IntcodeRunner(read_comma_separated_integers('day21input.txt'))

    def read_prompt(self):
        rtn = ''
        ch = self.ic.communicate()
        while ch != 10:
            rtn += chr(ch)
            ch = self.ic.communicate()
        return rtn

    def write_command(self, command):
        print(f'>{command}')
        for ch in command:
            self.ic.communicate(ord(ch))
        self.ic.communicate(10)

    def read_output(self):
        while not self.ic.finished:
            ch = self.ic.communicate()
            if ch is not None:
                if ch < 256:
                    print(chr(ch), end='')
                else:
                    return ch
        print(' ABCDEFGHI')



def puzzle1():
    programmer = SpringDroidProgrammer()
    print(programmer.read_prompt())
    programmer.write_command('NOT A J')
    programmer.write_command('NOT B T')
    programmer.write_command('OR T J')
    programmer.write_command('NOT C T')
    programmer.write_command('OR T J')
    programmer.write_command('AND D J')
    programmer.write_command('WALK')
    return programmer.read_output()



if __name__ == "__main__":
    assert puzzle1() == 19353074

