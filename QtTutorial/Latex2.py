"""
Editable math renderer: user edits named variables in QLineEdits,
the LaTeX is re-rendered live using matplotlib.
"""

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QVBoxLayout, QFormLayout
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import math
import sys

class MathEditableLabel(QtWidgets.QWidget):
    def __init__(self, math_template: str, variables: dict, parent=None):
        """
        math_template: a LaTeX string containing Python-format placeholders, e.g.
          r'$X_k = \sum_{n=0}^{{{N}}-1} x_n \, e^{{\frac{{-i2\pi k n}}{{{N}}}}}$'
        variables: dict of variable_name -> initial_value (strings are fine)
        """
        super().__init__(parent)
        self.math_template = math_template
        # store variable values as strings
        self.vars = {k: str(v) for k, v in variables.items()}

        main = QVBoxLayout(self)
        main.setContentsMargins(6, 6, 6, 6)

        # canvas area
        r, g, b, a = self.palette().base().color().getRgbF()
        self._figure = Figure(edgecolor=(r, g, b), facecolor=(r, g, b))
        self._canvas = FigureCanvas(self._figure)
        main.addWidget(self._canvas, stretch=1)

        # controls area where QLineEdits live
        form = QFormLayout()
        self._edits = {}
        for name, val in self.vars.items():
            le = QtWidgets.QLineEdit(val)
            le.setMaximumWidth(120)
            le.editingFinished.connect(self._make_on_edit_finished(name, le))
            form.addRow(f"{name}:", le)
            self._edits[name] = le
        main.addLayout(form)

        # initial render
        self._render_math()

    def _make_on_edit_finished(self, name, lineedit):
        def handler():
            self.vars[name] = lineedit.text()
            self._render_math()
        return handler

    def _render_math(self):
        # build the math string by formatting the template with current values
        try:
            math_text = self.math_template.format(**self.vars)
        except Exception as e:
            math_text = r"$\text{Format error: " + str(e).replace('}', '') + r"}$"

        # clear, render, and update widget size
        self._figure.clf()
        # add a full-figure axes so text placement is stable
        ax = self._figure.add_axes([0, 0, 1, 1])
        ax.axis('off')

        # place text at top-left of figure (figure coords)
        # use fontsize derived from Qt default font to match UI scale
        fontsize = QtGui.QFont().pointSize() * 2
        txt = self._figure.suptitle(math_text, x=0.0, y=1.0,
                                    horizontalalignment='left',
                                    verticalalignment='top',
                                    size=fontsize)

        # draw to create renderer and extents
        self._canvas.draw()

        # measure text extents (pixels)
        renderer = self._canvas.get_renderer()
        bbox = txt.get_window_extent(renderer=renderer)
        x0, y0 = bbox.x0, bbox.y0
        x1, y1 = bbox.x1, bbox.y1
        width = x1 - x0
        height = y1 - y0

        # set figure size in inches using DPI so rendering fits tightly
        dpi = self._figure.get_dpi()
        self._figure.set_size_inches(math.ceil(width / dpi), math.ceil(height / dpi))
        # redraw with final size
        self._canvas.draw()

        # set a reasonable fixed height for the canvas so layout stays stable.
        # Note: FigureCanvas size is in device pixels. Convert and ceil to integers.
        self._canvas.setFixedHeight(int(math.ceil(height)))
        self._canvas.setFixedWidth(int(math.ceil(width)))

# Example usage
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Template using formatting placeholders.
    # To include literal LaTeX braces around substituted values use doubled braces {{ and }}.
    math_template = (
        r'$X_{{k}} = \sum_{{n=0}}^{{{N}-1}} x_n \cdot '
        r'e^{{\frac{{-i2\pi k n}}{{{N}}}}}$'
    )

    # initial variables
    variables = {"N": 8, "k": 0}

    w = QtWidgets.QWidget()
    layout = QVBoxLayout(w)
    layout.setContentsMargins(12, 12, 12, 12)

    label = MathEditableLabel(math_template, variables)
    layout.addWidget(label, alignment=Qt.AlignHCenter)

    w.setWindowTitle("Editable Math Demo")
    w.show()
    w.resize(600, 200)
    sys.exit(app.exec_())
