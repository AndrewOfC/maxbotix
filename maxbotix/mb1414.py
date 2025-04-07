from datetime import datetime

from serial import Serial
import re

class Observer(object):
    def __init__(self):
        return

    def process_range(self, mb, valid, inches):
        raise NotImplementedError()


class MB1414(object):

    _match = re.compile(r"R([0-9]{3}) P([01])\r", re.MULTILINE)

    def __init__(self, serial_device):
        self._device = serial_device
        self._syncs = 0

    syncs = property(lambda self: self._syncs)

    def open(self):
        self._serial = Serial(self._device, baudrate=57600, bytesize=8, parity='N', stopbits=1)

    def _sychronize(self):
        synced = False
        self._syncs += 1
        while not synced :
            b = self._serial.read(1)
            synced = b == b'R'
        self._serial.read(7)

    def _read_one(self):
        #RXXX PX\n
        while True:
            s = self._serial.read(8)
            if s[0] != b'R'[0]:
                self._sychronize()
                continue
            # range = int(b'0'[0] + s[1]) * 100 + int(b'0'[0] + s[2]) * 10 + int(b'0'[0] + s[3])
            s = s.decode('ascii')
            m = self._match.match(s)
            if not m: # garbled, noise, etc
                self._sychronize()
                continue
            inches = int(m.group(1))
            valid = m.group(2) == '1'
            return valid, inches

    def loop(self, observer: Observer):
        running = True
        while running:
            valid, inches = self._read_one()
            running = observer.process_range(self, valid, inches)




class SimpleObserver(Observer):
    def process_range(self, mb, valid, inches):
        print(f"{valid} {inches}")
        return True

class MetricsObserver(Observer):
    def __init__(self):
        self._samples = 0
        self._time = datetime.now()

    def process_range(self, mb, valid, inches):
        self._samples += 1
        t0 = datetime.now()
        dt = t0 - self._time
        if dt.total_seconds() >= 5:
            print(f"{self._samples} {dt.total_seconds():.3f} {self._samples / dt.total_seconds():.3f} syncs = {mb.syncs} ")
            self._samples = 0
            self._time = t0
        return True



def main():
    mb1414 = MB1414('/dev/ttyUSB0')
    mb1414.open()

    mb1414.loop(MetricsObserver())

if __name__ == '__main__':
    main()


