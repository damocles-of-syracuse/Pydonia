import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListView, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Resizable File Viewer and Work Area")
        self.setGeometry(100, 100, 800, 600)

        # Create the file viewer (left)
        self.file_viewer = QListView()
        self.file_viewer.setMinimumWidth(100)

        # Create the work environment (right)
        self.work_area = QTextEdit()
        self.work_area.setPlaceholderText("Work area")

        # Create a horizontal splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.file_viewer)
        self.splitter.addWidget(self.work_area)

        # Optional: Set initial sizes
        self.splitter.setSizes([200, 600])

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
