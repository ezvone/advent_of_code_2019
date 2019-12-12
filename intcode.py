
from threading import Thread
from queue import Queue


class InfiniteMemory:
    def __init__(self, data):
        self.data = dict(enumerate(data))

    def __getitem__(self, index):
        index = int(index)
        assert index >= 0
        return self.data.get(index, 0)

    def __setitem__(self, index, value):
        index = int(index)
        value = int(value)
        assert index >= 0
        self.data[index] = value

    def __eq__(self, other):
        if isinstance(other, InfiniteMemory):
            return self.data == other.data


class Intcode:
    def __init__(self, opcodes):
        self.opcodes = InfiniteMemory(opcodes)

    def run(self):
        """run without any inputs, return list of outputs"""

        grun = self.run_generator()
        result = []
        for x in grun:
            if x is not None:
                result.append(x)
        return result

    def run_generator(self):
        """Run as a generator"""
        p = 0
        relative_base = 0
        ops = self.opcodes
        next_input = yield
        while True:
            op_value = ops[p]
            op = op_value % 100
            modes =  dict(enumerate(reversed(str(op_value//100))))
            def read(i):
                mode = modes.get(i-1, '0')
                assert mode in '012'
                if mode == '0':
                    return ops[ops[p+i]]
                elif mode == '1':
                    return ops[p+i]
                elif mode == '2':
                    return ops[relative_base+ops[p+i]]

            def write(i, value):
                mode = modes.get(i-1, '0')
                assert mode in '02'
                if mode == '0':
                    ops[ops[p+i]] = value
                elif mode == '2':
                    ops[relative_base+ops[p+i]] = value

            if op == 1:
                write(3, read(1) + read(2))
                p += 4
            elif op == 2:
                write(3, read(1) * read(2))
                p += 4
            elif op == 3:
                v = int(next_input)
                next_input = yield
                write(1, v)
                p += 2
            elif op == 4:
                v = read(1)
                if next_input is not None:
                    yield
                next_input = yield v
                p += 2
            elif op == 5:
                if read(1):
                    p = read(2)
                else:
                    p += 3
            elif op == 6:
                if not read(1):
                    p = read(2)
                else:
                    p += 3
            elif op == 7:
                if read(1) < read(2):
                    write(3, 1)
                else:
                    write(3, 0)
                p += 4
            elif op == 8:
                if read(1) == read(2):
                    write(3, 1)
                else:
                    write(3, 0)
                p += 4
            elif op == 9:
                relative_base += read(1)
                p += 2
            elif op == 99:
                return
            else:
                raise Exception(f'Invalid opcode {op}')


class IntcodeRunner:
    """Simpler abstraction above low-level python generator handling

    Probably useless...
    """
    def __init__(self, opcodes):
        self.ic = Intcode(opcodes)
        self.gen = self.ic.run_generator()
        self.finished = False
        next(self.gen)

    def communicate(self, input_value=None):
        """May send input, read output, or do neither :)"""
        try:
            return self.gen.send(input_value)
        except StopIteration:
            self.finished = True
            return None
