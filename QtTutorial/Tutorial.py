# pyside6-designer
# pyuic6 -x .\WindowDesign.ui -o filename.py
import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("Pydonia")
        self.initUI()

    def initUI(self):
        # label
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Label")
        self.label.move(50, 50)

        # Button
        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setGeometry(100, 100, 50, 30)
        self.b1.setText("Click")
        self.b1.clicked.connect(self.clicked)

    def clicked(self):
        self.label.setText("Button Pressed --------------------asfgh")
        self.updateLabel()

    def updateLabel(self):
        self.label.adjustSize()


def window():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())


def main():
    window()

if __name__ == "__main__":
    main()