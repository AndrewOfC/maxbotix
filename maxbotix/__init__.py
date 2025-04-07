

import os, sys

from PyQt5.QtCore import QThread, QLocale, pyqtSignal, pyqtSlot, QObject

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import maxbotix.mb1414 as mb

from PyQt5.QtWidgets import *

class MBThread(QThread, mb.Observer):

    sensor_reading = pyqtSignal(bool, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mb = mb.MB1414('/dev/ttyUSB0')
        self.mb.open()

    def process_range(self, valid, inches):
        print(f"{valid} {inches}")
        # self.sensor_reading.emit(valid, inches)

        return

    def run(self):
        self.mb.loop(self)


class MBWindow(QObject):
    def __init__(self, geometry=(500, 100, 600, 600)):
        super().__init__()
        self._mainw = mainw = QMainWindow()

        layout = QGridLayout()
        central = QWidget()
        central.setLayout(layout)

        mainw.setCentralWidget(central)

        label = QLabel("Valid:")
        layout.addWidget(label, 0, 0)

        self._validWidget = QLabel()
        layout.addWidget(self._validWidget, 0, 1)

        label = QLabel("Inches:")
        layout.addWidget(label, 1, 0)

        self._inchesWidget = QLabel()

        self._thread = MBThread()

        self._thread.sensor_reading[bool, int].connect(self._display)

        self._thread.start()
        return

    def show(self):
        self._mainw.show()

    @pyqtSlot(bool, int)
    def _display(self, valid, inches):
        self._validWidget.setText(str(valid))
        self._inchesWidget.setText(str(inches))

def main():
    app = QApplication(sys.argv)

    mbw = MBWindow()

    mbw.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
