from collections import deque

from input_reader import read_comma_separated_integers
from intcode import Intcode


class NetworkInterfaceController:
    def __init__(self, address):
        self.address = address
        self.input_q = deque()
        self._idle_counter = 0
        self.ic = Intcode(read_comma_separated_integers('day23input.txt'))
        self.ic.start()
        self.ic.write_input(address)

    def __repr__(self):
        return f'<NIC {self.address!r}>'

    def communicate(self, network):
        if self.ic.requires_input:
            if self.input_q:
                self.ic.write_input(self.input_q.popleft())
                self._idle_counter = 0
            else:
                self.ic.write_input(-1)
                self._idle_counter += 1
        else:
            # if it is not taking an input, assume it has 3 outputs
            addr = self.ic.read_output()
            x = self.ic.read_output()
            y = self.ic.read_output()
            network.transmit(self.address, addr, x, y)
            self._idle_counter = 0

    def receive(self, x, y):
        self.input_q.append(x)
        self.input_q.append(y)

    def is_idle(self):
        return self._idle_counter > 50


class NotAlwaysTransmitting:
    def __init__(self):
        self.x = None
        self.y = None

    def receive(self, x, y):
        self.x = x
        self.y = y

    def is_idle(self):
        return True

    def communicate(self, network):
        if network.is_idle():
            network.transmit(255, 0, self.x, self.y)


class Network:
    def __init__(self):
        self.computers = {
            address: NetworkInterfaceController(address)
            for address in range(50)}
        self.computers[255] = NotAlwaysTransmitting()
        self._observers = []

    def observe_transmissions(self, callback):
        """callback takes 4 args: sender, recipient, x, y"""
        self._observers.append(callback)

    def transmit(self, sender, recipient, x, y):
        self.computers[recipient].receive(x, y)
        for observer in self._observers:
            observer(sender, recipient, x, y)

    def loop(self):
        for computer in self.computers.values():
            computer.communicate(self)

    def is_idle(self):
        return all(c.is_idle() for c in self.computers.values())


def puzzle1():
    network = Network()
    result = None

    def observe_255_y(sender, recipient, x, y):
        nonlocal result
        if result is None and recipient == 255:
            result = y

    network.observe_transmissions(observe_255_y)

    while result is None:
        network.loop()
    return result


def puzzle2():
    network = Network()
    last_y = None
    double_y = None

    def observe_255_y(sender, recipient, x, y):
        nonlocal last_y
        nonlocal double_y
        if double_y is None and sender == 255:
            if last_y == y:
                double_y = y
            last_y = y

    network.observe_transmissions(observe_255_y)

    while double_y is None:
        network.loop()
    return double_y


if __name__ == "__main__":
    assert puzzle1() == 17740
    assert puzzle2() == 12567
    print('OK.')
