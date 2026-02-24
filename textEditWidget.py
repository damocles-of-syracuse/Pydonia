from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QTextEdit
from PyQt6.uic.Compiler.qtproxies import QtWidgets


class TextEdit(QTextEdit):
    cellRunRequest = pyqtSignal(QTextEdit)
    deleteRequested = pyqtSignal(QTextEdit) # cannot use QtWidgets.QWidget because QWidget is an ancestor not a parent

    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        # print(f"Key pressed: {event.key()}, {event.modifiers()}")

        # Check if Shift + Enter is pressed
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier and event.key() == Qt.Key.Key_Return:
            self.cellRunRequest.emit(self)
            event.accept()
            return
        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier and event.key() == Qt.Key.Key_Backspace:
            self.deleteRequested.emit(self)
            event.accept()
            return
        else:
            super().keyPressEvent(event)