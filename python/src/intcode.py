from enum import Enum
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


class _IntcodeState(Enum):
    NOT_STARTED = 1
    OUTPUT_READY = 2
    WAITING_FOR_INPUT = 3
    INTERMEDIATE = 4
    FINISHED = 5


class IntcodeError(Exception):
    pass


class Intcode:
    """Intcode interpreter

    Typical usage example:

        ic = Intcode(code_bytes)
        ic.start()
        ic.write_input(44)
        while not ic.finished:
            print(ic.read_output())

    """
    def __init__(self, opcodes):
        self.memory = InfiniteMemory(opcodes)
        self._state = _IntcodeState.NOT_STARTED
        self._generator = None

    @property
    def finished(self):
        return self._state == _IntcodeState.FINISHED

    @property
    def has_output(self):
        return self._state == _IntcodeState.OUTPUT_READY

    @property
    def requires_input(self):
        return self._state == _IntcodeState.WAITING_FOR_INPUT

    def start(self):
        self._assert_state(_IntcodeState.NOT_STARTED)
        self._generator = self._run_generator()
        self._step()

    def read_output(self):
        self._assert_state(_IntcodeState.OUTPUT_READY)

        rtn = next(self._generator)
        assert isinstance(rtn, int)
        assert self._state == _IntcodeState.INTERMEDIATE
        self._step()
        return rtn

    def write_input(self, value):
        if not isinstance(value, int):
            raise TypeError("value must be an integer")

        self._assert_state(_IntcodeState.WAITING_FOR_INPUT)
        self._step(value)

    def _assert_state(self, expected_state):
        if self._state == expected_state:
            return

        if expected_state == _IntcodeState.NOT_STARTED:
            raise IntcodeError("Intcode already started.")
        if self._state == _IntcodeState.NOT_STARTED:
            raise IntcodeError(
                "Intcode not yet started. Call start() to start it.")
        if self._state == _IntcodeState.FINISHED:
            raise IntcodeError(
                "Intcode finished. No operation on it is possible.")
        if expected_state == _IntcodeState.WAITING_FOR_INPUT:
            raise IntcodeError("Intcode is not currently expecting input")
        if expected_state == _IntcodeState.OUTPUT_READY:
            raise IntcodeError("Intcode is not currently providing output")
        raise IntcodeError(f"Intcode is in state {self._state} "
                           f"and {expected_state} is expected.")

    def _step(self, send_value=None):
        try:
            self._generator.send(send_value)
        except StopIteration:
            self._state = _IntcodeState.FINISHED

    def _run_generator(self):
        p = 0
        relative_base = 0
        ops = self.memory
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
                self._state = _IntcodeState.WAITING_FOR_INPUT
                v = yield
                write(1, v)
                p += 2
            elif op == 4:
                v = read(1)
                self._state = _IntcodeState.OUTPUT_READY
                yield
                self._state = _IntcodeState.INTERMEDIATE
                yield v
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

