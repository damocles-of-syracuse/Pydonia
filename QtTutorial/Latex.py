# Source - https://stackoverflow.com/a
# Posted by Jlondono, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-07, License - CC BY-SA 4.0

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import math

class MathTextLabel(QtWidgets.QWidget):
    def __init__(self, mathText, parent=None, **kwargs):
        super().__init__(parent, **kwargs)              # fixed super() call

        l = QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)

        r, g, b, a = self.palette().base().color().getRgbF()
        self._figure = Figure(edgecolor=(r, g, b), facecolor=(r, g, b))
        self._canvas = FigureCanvas(self._figure)
        l.addWidget(self._canvas)

        self._figure.clear()
        text = self._figure.suptitle(
            mathText,
            x=0.0,
            y=1.0,
            horizontalalignment='left',
            verticalalignment='top',
            size=QtGui.QFont().pointSize() * 2
        )
        self._canvas.draw()  # draw to create the text extents

        # extents come back as floats (pixels). Convert properly to ints.
        (x0, y0), (x1, y1) = text.get_window_extent().get_points()
        w = x1 - x0
        h = y1 - y0

        # use the figure DPI instead of magic number 80
        dpi = self._figure.get_dpi()
        self._figure.set_size_inches(w / dpi, h / dpi)

        # redraw after changing figure size (optional but safe)
        self._canvas.draw()

        # set a fixed widget size in whole pixels (integers)
        self.setFixedSize(int(math.ceil(w)), int(math.ceil(h)))


if __name__=='__main__':
    from sys import argv, exit

    class Widget(QtWidgets.QWidget):
        def __init__(self, parent=None, **kwargs):
            super(QtWidgets.QWidget, self).__init__(parent, **kwargs)

            l=QVBoxLayout(self)
            mathText=r'$X_k = \sum_{n=0}^{N-1} x_n . e^{\frac{-i2\pi kn}{N}}$'
            l.addWidget(MathTextLabel(mathText, self), alignment=Qt.AlignHCenter)

    a=QtWidgets.QApplication(argv)
    w=Widget()
    w.show()
    w.raise_()
    exit(a.exec_())
