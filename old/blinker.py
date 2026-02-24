# blinker.py
import time
from PyQt6.QtCore import QThread, pyqtSignal

class Blinker(QThread):
    blink = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True

    def run(self):
        while self._running:
            self.blink.emit(".")
            time.sleep(0.5)
            if not self._running:
                break
            self.blink.emit(". .")
            time.sleep(0.5)
            if not self._running:
                break
            self.blink.emit(". . .")
            time.sleep(0.5)

    def stop(self):
        self._running = False