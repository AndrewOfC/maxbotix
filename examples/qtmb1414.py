

import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QMutex, QMutexLocker, QWaitCondition, pyqtSignal, pyqtSlot, Qt, QObject

import maxbotix.mb1414 as mb

class MBThread(QThread, mb.Observer):

    sensor_reading = pyqtSignal(bool, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._mb = mb.MB1414('/dev/ttyUSB0')

        self._mb.open()

    def run(self):
        self._mb.loop(self)

    def process_range(self, mb, valid, inches):
        self.sensor_reading[bool, int].emit(valid, inches)

        return True

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
        self._inchWidget = QLabel()
        layout.addWidget(self._inchWidget, 1, 1)

        self._thread = MBThread()

        self._thread.sensor_reading[bool, int].connect(self._display)

        self._thread.start()


    def show(self):
        self._mainw.show()

    @pyqtSlot(bool, int)
    def _display(self, valid, inches):
        self._validWidget.setText(str(valid))
        self._inchWidget.setText(str(inches))


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(" * {font-size: 72px; font: \"Times New Roman 72\"}")
    window = MBWindow()

    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()